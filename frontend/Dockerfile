# SPDX-License-Identifier: AGPL-3.0-or-later
# biohack.it — open-source biohacking platform
# Copyright (C) HackingBiology 2026 — https://biohack.it

FROM node:20-slim AS base
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

WORKDIR /app

FROM base AS deps
COPY package.json pnpm-lock.yaml* ./
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm install --frozen-lockfile

FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ARG BACKEND_INTERNAL_URL=http://backend:8000
ARG NOINDEX=0
ENV BACKEND_INTERNAL_URL=$BACKEND_INTERNAL_URL
ENV NOINDEX=$NOINDEX
RUN pnpm build

FROM base AS runner
ENV NODE_ENV=production
WORKDIR /app
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
