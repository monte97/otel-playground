FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /app

# Copy csproj and restore dependencies
COPY invoice-app/*.csproj ./
RUN dotnet restore

# Copy the rest of the application and build it
COPY invoice-app/. ./
RUN dotnet publish -c Release -p:AssemblyName=invoice -o /out

# Use a smaller runtime image
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /out .

# Expose the port and run the API
EXPOSE 8000
ENTRYPOINT ["dotnet", "invoice.dll"]
