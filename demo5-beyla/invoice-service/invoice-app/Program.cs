using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using System.Net.Http;
using System.Threading.Tasks;
using OpenTelemetry;
using OpenTelemetry.Logs;
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;

var builder = WebApplication.CreateBuilder(args);

// Register HttpClient for making external HTTP requests.
builder.Services.AddHttpClient();

// OpenTelemetry Configuration
builder.Services.AddOpenTelemetry()
    .ConfigureResource(resource => resource.AddService("Simple-Get-Service"))
    .WithMetrics(metrics =>
    {
        metrics.AddAspNetCoreInstrumentation()
               .AddHttpClientInstrumentation()
               .AddOtlpExporter();
    })
    .WithTracing(tracing =>
    {
        tracing.AddAspNetCoreInstrumentation()
               .AddHttpClientInstrumentation()
               .AddOtlpExporter();
    });

// Configure logging to export logs via OpenTelemetry.
builder.Logging.AddOpenTelemetry(logging => logging.AddOtlpExporter());

var app = builder.Build();

// Read the external endpoint from the environment variable
var externalPingUrl = builder.Configuration["EXTERNAL_PING_URL"] ?? "https://example.com/ping";

// Single GET endpoint that makes a request to the external endpoint before returning a response.
app.MapGet("/call", async (IHttpClientFactory clientFactory) =>
{
    var client = clientFactory.CreateClient();
    var response = await client.GetAsync(externalPingUrl);
    var content = await response.Content.ReadAsStringAsync();

    app.Logger.LogInformation("Called external endpoint '{ExternalUrl}' and received response: {Content}", externalPingUrl, content);

    return Results.Ok(new { message = "Response from external endpoint", externalResponse = content });
});

app.Run();
