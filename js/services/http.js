/*
HolyricsExtractor: A lightweight tool to search, extract, and format song lyrics for Holyrics.
Copyright (C) 2026 @xorodev (CipherCoreDev)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

Third-Party Dependencies & Credits:
- Built with Python (https://www.python.org/)
- Metadata extraction powered by yt-dlp (https://github.com/yt-dlp/yt-dlp)
- HTTP requests powered by Requests (https://requests.readthedocs.io)
- Lyrics API provided by LRCLIB (https://lrclib.net)
- Graphic Assets & Icons: Created from scratch by @xorodev

GitHub: https://github.com/xorodev/HolyricsExtractor
Contact:
a. Email: corex.dev@proton.me
b. Telegram: https://t.me/xorodev
*/
import {
  LRCLIB_SEARCH_URL,
  MAX_API_RESPONSE_BYTES,
  MAX_RETRIES,
  REQUEST_TIMEOUT_MS,
  RETRYABLE_STATUSES,
  RETRY_BACKOFF_MS,
  YOUTUBE_OEMBED_URL,
} from '../config/constants.js';
import { AppError, NetworkError, OperationCancelled, ServiceResponseError } from '../core/errors.js';

const ALLOWED_HOSTS = new Set([LRCLIB_SEARCH_URL, YOUTUBE_OEMBED_URL].map((url) => new URL(url).hostname));

class RetryableResponseError extends ServiceResponseError {}

function buildUrl(base, params) {
  const url = new URL(base);
  if (url.protocol !== 'https:' || !ALLOWED_HOSTS.has(url.hostname)) {
    throw new ServiceResponseError(`Blocked request to ${url.hostname}`);
  }
  for (const [name, value] of Object.entries(params)) url.searchParams.set(name, value);
  return url;
}

function sleep(milliseconds, signal) {
  return new Promise((resolve, reject) => {
    const onAbort = () => {
      clearTimeout(timer);
      reject(new OperationCancelled());
    };
    const timer = setTimeout(() => {
      signal.removeEventListener('abort', onAbort);
      resolve();
    }, milliseconds);
    signal.addEventListener('abort', onAbort, { once: true });
  });
}

async function readLimitedText(response, host) {
  const declared = Number(response.headers.get('Content-Length'));
  if (Number.isFinite(declared) && declared > MAX_API_RESPONSE_BYTES) {
    throw new ServiceResponseError(`Response from ${host} exceeds ${MAX_API_RESPONSE_BYTES} bytes`);
  }
  if (response.body === null) throw new ServiceResponseError(`Empty response body from ${host}`);
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let text = '';
  let total = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) return text + decoder.decode();
    total += value.byteLength;
    if (total > MAX_API_RESPONSE_BYTES) {
      await reader.cancel();
      throw new ServiceResponseError(`Response from ${host} exceeds ${MAX_API_RESPONSE_BYTES} bytes`);
    }
    text += decoder.decode(value, { stream: true });
  }
}

async function requestJson(url, signal) {
  const attempt = new AbortController();
  const forwardAbort = () => attempt.abort(signal.reason);
  signal.addEventListener('abort', forwardAbort, { once: true });
  const timer = setTimeout(
    () => attempt.abort(new DOMException('Request timed out', 'TimeoutError')),
    REQUEST_TIMEOUT_MS,
  );
  try {
    const response = await fetch(url, {
      method: 'GET',
      mode: 'cors',
      credentials: 'omit',
      referrerPolicy: 'no-referrer',
      headers: { Accept: 'application/json' },
      signal: attempt.signal,
    });
    if (response.status === 404) {
      await response.body?.cancel();
      return null;
    }
    if (response.status !== 200) {
      await response.body?.cancel();
      const ErrorType = RETRYABLE_STATUSES.includes(response.status) ? RetryableResponseError : ServiceResponseError;
      throw new ErrorType(`HTTP ${response.status} from ${url.hostname}`);
    }
    const text = await readLimitedText(response, url.hostname);
    try {
      return JSON.parse(text);
    } catch {
      throw new ServiceResponseError('Invalid JSON payload');
    }
  } catch (error) {
    if (signal.aborted) throw new OperationCancelled();
    if (error instanceof AppError) throw error;
    throw new NetworkError(`${url.hostname}: ${error instanceof Error ? error.name : 'RequestFailed'}`);
  } finally {
    clearTimeout(timer);
    signal.removeEventListener('abort', forwardAbort);
  }
}

function isRetryable(error) {
  return error instanceof NetworkError || error instanceof RetryableResponseError;
}

export async function fetchJson(base, params, signal) {
  const url = buildUrl(base, params);
  for (let attempt = 0; ; attempt += 1) {
    signal.throwIfAborted();
    try {
      return await requestJson(url, signal);
    } catch (error) {
      if (!isRetryable(error) || attempt >= MAX_RETRIES) throw error;
      await sleep(RETRY_BACKOFF_MS * 2 ** attempt, signal);
    }
  }
}