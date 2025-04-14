# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV IS_DOCKER_ENV=true
ENV CHROME_VERSION="114.0.5735.198-1"

# Create a non-root user
RUN useradd -m -u 1000 scraper

# Install system dependencies required for Chrome and undetected-chromedriver
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    # Add Chrome repository
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    # Install Chrome
    && apt-get update && apt-get install -y google-chrome-stable=${CHROME_VERSION} --no-install-recommends \
    # Install additional dependencies
    && apt-get install -y --no-install-recommends \
    libx11-xcb1 \
    libxss1 \
    libxtst6 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    # Clean up
    && rm -rf /var/lib/apt/lists/* \
    # Fix Chrome sandbox issues
    && mkdir -p /home/scraper/.config/chrome-sandbox \
    && chown -R scraper:scraper /home/scraper

# Create Chrome user data directory and set permissions
RUN mkdir -p /home/scraper/.config/chrome && \
    chown -R scraper:scraper /home/scraper/.config

# Create data directory for screenshots and other files
RUN mkdir -p /app/data/screenshots && \
    chown -R scraper:scraper /app/data

# Set the working directory in the container
WORKDIR /app

# Install Python dependencies
# Copy only requirements.txt first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set correct permissions
RUN chown -R scraper:scraper /app

# Switch to non-root user
USER scraper

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the application
# Use 0.0.0.0 to make it accessible from outside the container
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"] 