# Copyright 2025 SyncFlow Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM python:3.11-slim

# Install uv package manager
RUN pip install --no-cache-dir uv

WORKDIR /code

# Copy project files
COPY ./pyproject.toml ./README.md ./uv.lock* ./

# Copy application code
COPY ./app ./app

# Install dependencies
RUN uv sync --frozen

# Expose port
EXPOSE 8080

# Run the application
CMD ["uv", "run", "uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8080"]
