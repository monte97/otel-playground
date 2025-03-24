# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy the project file and restore dependencies
COPY MyApi/*.csproj MyApi/
RUN dotnet restore MyApi/App.csproj

# Copy the remaining source code and publish the application
COPY MyApi/ MyApi/
WORKDIR /src/MyApi
RUN dotnet publish -c Release -o /app/publish

# Stage 2: Runtime
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .

ENV ASPNETCORE_URLS=http://+:8000

# Expose the port your application listens on (adjust if necessary)
EXPOSE 8000

# Run the application (ensure the DLL name matches your published output)
ENTRYPOINT ["dotnet", "App.dll"]
