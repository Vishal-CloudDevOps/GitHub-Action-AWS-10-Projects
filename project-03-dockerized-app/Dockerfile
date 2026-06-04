# ============================================================
# Multi-Stage Dockerfile — Project 03
# ============================================================
# WHY MULTI-STAGE?
#   - Stage 1 installs ALL dependencies (including dev tools)
#   - Stage 2 (production) copies only what's needed
#   - Result: production image is smaller and has fewer attack surfaces
#
# SIZE COMPARISON:
#   Single-stage with dev deps: ~700MB
#   Multi-stage production:     ~180MB
# ============================================================

# ── Stage 1: Builder ─────────────────────────────────────────
# Use a full Node.js image to install everything
FROM node:20-alpine AS builder

# Set working directory inside the container
WORKDIR /app

# Copy dependency manifests FIRST (before source code)
# Why? Docker layer caching: if package.json hasn't changed,
# `npm ci` is skipped on rebuild — saves significant time
COPY package*.json ./

# Install ALL dependencies (including devDependencies for potential build steps)
# `npm ci` is preferred in CI/Docker: uses exact lockfile, faster, reproducible
RUN npm ci

# Now copy source code (this layer changes most often — put it last)
COPY src/ ./src/

# ── Stage 2: Test ────────────────────────────────────────────
# Run tests inside Docker to ensure they pass in the container environment
FROM builder AS tester

# Copy test files
COPY tests/ ./tests/

# Run tests — if they fail, the build fails here before producing an image
RUN npm test -- --forceExit

# ── Stage 3: Production ──────────────────────────────────────
# Start fresh from the slim base image
FROM node:20-alpine AS production

# Security: Don't run as root
# Create a dedicated non-root user and group
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Set working directory
WORKDIR /app

# Copy only package manifests for production install
COPY package*.json ./

# Install ONLY production dependencies (no jest, nodemon, etc.)
# --omit=dev removes devDependencies
# && npm cache clean --force removes cached install files
RUN npm ci --omit=dev && npm cache clean --force

# Copy compiled/source application from builder stage
# (NOT from tester, to avoid including test files in the final image)
COPY --from=builder /app/src ./src

# Set ownership of all files to the non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user for all subsequent commands and at runtime
USER appuser

# OCI standard labels — helps with image management and traceability
LABEL org.opencontainers.image.title="project-03-dockerized-app" \
      org.opencontainers.image.description="Dockerized Node.js app for CI/CD learning" \
      org.opencontainers.image.vendor="github-actions-aws-cicd-learning"

# Expose the port the app listens on
# Note: EXPOSE is documentation only — you still need -p when running
EXPOSE 8080

# Health check built into the image
# Docker (and ECS) use this to determine if the container is healthy
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD wget -qO- http://localhost:8080/health || exit 1

# The command to run when the container starts
# Use exec form (JSON array) so signals (SIGTERM) are passed directly to Node
CMD ["node", "src/app.js"]
