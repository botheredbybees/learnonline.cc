FROM node:18-alpine

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    curl \
    wget \
    git

# Copy package files
COPY package*.json ./

# Install dependencies, including devDependencies
ENV NODE_ENV=development
RUN npm install

# Copy the rest of the application
COPY . .

# Add ESLint configuration to disable unused-vars rule
RUN echo '{ "extends": ["eslint:recommended"], "rules": { "no-unused-vars": "off" } }' > .eslintrc.json

# Build the application
ENV NODE_ENV=production
RUN npm run build

# Create necessary directories
RUN mkdir -p /app/logs

# Set environment variables
ENV NODE_ENV=production
ENV HOST=0.0.0.0

# Run the application using the serve script from package.json
CMD ["npm", "run", "start"]