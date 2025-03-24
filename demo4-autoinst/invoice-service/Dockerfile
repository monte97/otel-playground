# Use official .NET SDK image for building the app
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build

WORKDIR /app

# Copy project files and restore dependencies
COPY MyApi/*.csproj ./
RUN dotnet restore

# Copy everything else and build the app
COPY MyApi/. ./
RUN dotnet publish -c Release -o /out

# Use runtime image for final container
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime

WORKDIR /app

# Copy published files from build stage
COPY --from=build /out ./

RUN apt update && apt install wget curl zip -y
RUN mkdir /otel
RUN curl -L -o /otel/otel-dotnet-install.sh https://github.com/open-telemetry/opentelemetry-dotnet-instrumentation/releases/download/v1.11.0/otel-dotnet-auto-install.sh
RUN chmod +x /otel/otel-dotnet-install.sh

ENV OTEL_DOTNET_AUTO_HOME=/otel
RUN /bin/bash /otel/otel-dotnet-install.sh

run chmod +x /otel/instrument.sh

# Expose port
EXPOSE 8000

# Set the entrypoint 
#ENTRYPOINT ["dotnet", "App.dll"]
ENTRYPOINT ["/bin/bash", "-c", "source /otel/instrument.sh && dotnet App.dll"]