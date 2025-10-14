# Frontend Dockerfile - React + TypeScript + Vite
FROM node:20-slim

# Metadata
LABEL maintainer="Malackathon 2025 Team"
LABEL description="React Frontend with Vite"

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Start development server with host binding
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
