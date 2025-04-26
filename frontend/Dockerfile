FROM node:16-alpine

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    curl \
    wget \
    git

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Build the application
RUN npm run build

# Install serve to run the application
RUN npm install -g serve

# Create necessary directories
RUN mkdir -p /app/logs

# Set environment variables
ENV NODE_ENV=production

# Run the application
CMD ["serve", "-s", "dist", "-l", "8080"] 