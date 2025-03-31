using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using OpenTelemetry;
using OpenTelemetry.Logs;
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;

var builder = WebApplication.CreateBuilder(args);

// Configure database
builder.Services.AddDbContext<InvoiceDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));

// Add Swagger
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// OpenTelemetry Configuration
builder.Services.AddOpenTelemetry()
    .ConfigureResource(resource => resource.AddService("Invoice-Service"))
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
               .AddEntityFrameworkCoreInstrumentation()
               .AddSource("Npgsql") // Traccia anche le query PostgreSQL
               .AddOtlpExporter();
    });

builder.Logging.AddOpenTelemetry(logging => logging.AddOtlpExporter());

var app = builder.Build();

app.UseSwagger();
app.UseSwaggerUI();

// Apply migrations at startup
using (var scope = app.Services.CreateScope())
{
    var dbContext = scope.ServiceProvider.GetRequiredService<InvoiceDbContext>();
    dbContext.Database.Migrate();
}

// API Endpoints
app.MapPost("/invoices", async ([FromBody] Invoice invoice, InvoiceDbContext db, ILogger<Program> logger) =>
{
    invoice.Id = Guid.NewGuid();
    logger.LogInformation("Creating a new invoice for {CustomerName}, Amount: {Amount}", invoice.CustomerName, invoice.Amount);
    
    db.Invoices.Add(invoice);
    await db.SaveChangesAsync();
    
    logger.LogInformation("Invoice {InvoiceId} created successfully", invoice.Id);
    return Results.Created($"/invoices/{invoice.Id}", invoice);
});

app.MapGet("/invoices", async (InvoiceDbContext db) => Results.Ok(await db.Invoices.ToListAsync()));

app.MapGet("/invoices/{id}", async (Guid id, InvoiceDbContext db) =>
{
    var invoice = await db.Invoices.FindAsync(id);
    return invoice is not null ? Results.Ok(invoice) : Results.NotFound();
});

app.MapPut("/invoices/{id}", async (Guid id, [FromBody] Invoice updatedInvoice, InvoiceDbContext db) =>
{
    var invoice = await db.Invoices.FindAsync(id);
    if (invoice is null) return Results.NotFound();
    
    invoice.CustomerName = updatedInvoice.CustomerName;
    invoice.Amount = updatedInvoice.Amount;
    invoice.DueDate = updatedInvoice.DueDate;
    await db.SaveChangesAsync();
    return Results.Ok(invoice);
});

app.MapDelete("/invoices/{id}", async (Guid id, InvoiceDbContext db) =>
{
    var invoice = await db.Invoices.FindAsync(id);
    if (invoice is null) return Results.NotFound();
    
    db.Invoices.Remove(invoice);
    await db.SaveChangesAsync();
    return Results.NoContent();
});

app.MapGet("/ping", () => Results.Ok("pong"));

app.Run();

// Database context
class InvoiceDbContext : DbContext
{
    public InvoiceDbContext(DbContextOptions<InvoiceDbContext> options) : base(options) { }
    public DbSet<Invoice> Invoices { get; set; }
}

// Invoice model
class Invoice
{
    public Guid Id { get; set; }
    public string CustomerName { get; set; } = string.Empty;
    public decimal Amount { get; set; }
    public DateTime DueDate { get; set; }
}
