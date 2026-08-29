/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_ROSBRIDGE_URL: string;
  readonly VITE_API_URL: string;
  readonly VITE_BLUE_TEAM_PASSWORD?: string;
  readonly VITE_RED_TEAM_PASSWORD?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
