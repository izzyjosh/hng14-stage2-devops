FROM node:18-alpine

# prevent npm from running unnecessary scripts during installation
ENV NODE_ENV=production

# system dependencies
RUN apk add --no-cache curl

# add us1er and group to run the app
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# set the working directory
WORKDIR /app

# install dependencies
COPY package*.json ./
RUN npm install --only=production

# copy app source code
COPY . .

# change ownership of the app files to the non-root user
RUN chown -R appuser:appgroup /app

# switch to the non-root user
USER appuser

# expose the port the app runs on
EXPOSE 3000

# health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# start the app
CMD ["npm", "start"]