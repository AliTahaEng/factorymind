type MessageCallback = (data: unknown) => void;
type ErrorCallback = (error: Event) => void;

const BASE_DELAY = 1000; // 1s
const MAX_DELAY = 30000; // 30s

export class WebSocketManager {
  private ws: WebSocket | null = null;
  private token: string | null = null;
  private messageCallbacks: MessageCallback[] = [];
  private errorCallbacks: ErrorCallback[] = [];
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private attempt = 0;
  private shouldReconnect = false;

  connect(token: string): void {
    this.token = token;
    this.shouldReconnect = true;
    this.attempt = 0;
    this._open();
  }

  disconnect(): void {
    this.shouldReconnect = false;
    if (this.reconnectTimer !== null) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  onMessage(cb: MessageCallback): () => void {
    this.messageCallbacks.push(cb);
    return () => {
      this.messageCallbacks = this.messageCallbacks.filter((fn) => fn !== cb);
    };
  }

  onError(cb: ErrorCallback): () => void {
    this.errorCallbacks.push(cb);
    return () => {
      this.errorCallbacks = this.errorCallbacks.filter((fn) => fn !== cb);
    };
  }

  private _open(): void {
    if (!this.token) return;
    const wsBase = process.env.NEXT_PUBLIC_WS_URL ?? 'ws://localhost:8000';
    const url = `${wsBase}/ws/live-feed?token=${this.token}`;
    const ws = new WebSocket(url);
    this.ws = ws;

    ws.onopen = () => {
      this.attempt = 0;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data as string);
        this.messageCallbacks.forEach((cb) => cb(data));
      } catch {
        // ignore malformed JSON
      }
    };

    ws.onerror = (event) => {
      this.errorCallbacks.forEach((cb) => cb(event));
    };

    ws.onclose = () => {
      this.ws = null;
      if (this.shouldReconnect) {
        const delay = Math.min(BASE_DELAY * 2 ** this.attempt, MAX_DELAY);
        this.attempt += 1;
        this.reconnectTimer = setTimeout(() => this._open(), delay);
      }
    };
  }
}

export const wsManager = new WebSocketManager();
