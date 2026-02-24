import { defineConfig } from "vite";
import { resolve } from "path";

export default defineConfig({
  server: {
    host: true,
    port: 3000,
  },
  build: {
    rollupOptions: {
      input: {
        root: resolve(__dirname, "index.html"),
        login: resolve(__dirname, "login/index.html"),
        admin: resolve(__dirname, "admin/index.html"),
        gerente: resolve(__dirname, "gerente/index.html"),
        funcionario: resolve(__dirname, "funcionario/index.html"),
      },
    },
  },
});
