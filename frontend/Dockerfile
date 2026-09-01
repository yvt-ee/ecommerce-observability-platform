FROM node:20-alpine

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

EXPOSE 5173

# Runs the Vite dev server so the demo stays a single, simple image
# (no separate nginx/build stage needed for a 1-2 day project).
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
