# =============================================================================
# AIOS QUANTUM VISUALIZER - PRODUCTION DOCKERFILE
# =============================================================================
# Multi-stage build for production deployment
# Stage 1: Build Next.js app
# Stage 2: Serve with nginx
# =============================================================================

# ---- Build Stage ----
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY web/package*.json ./

# Install dependencies
RUN npm ci --only=production=false

# Copy source
COPY web/ ./

# Build Next.js static export
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

RUN npm run build

# ---- Production Stage ----
FROM nginx:alpine AS production

# Install useful tools
RUN apk add --no-cache curl jq

# Copy nginx config
COPY docker/nginx.conf /etc/nginx/nginx.conf

# Copy built app
COPY --from=builder /app/out /usr/share/nginx/html

# Copy quantum data (experiments, heartbeats)
COPY web/public/quantum_experiments.json /usr/share/nginx/html/

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Metadata labels
LABEL org.opencontainers.image.title="AIOS Quantum Visualizer"
LABEL org.opencontainers.image.description="3D quantum consciousness hypersphere visualization"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/Tecnocrat/aios-quantum"
LABEL maintainer="AIOS Team"

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
