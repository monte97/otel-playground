CREATE TABLE IF NOT EXISTS "Invoices" (
    "Id" UUID PRIMARY KEY,
    "CustomerName" VARCHAR(255) NOT NULL,
    "Amount" DECIMAL NOT NULL,
    "DueDate" DATE NOT NULL
);