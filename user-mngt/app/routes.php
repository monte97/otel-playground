<?php
// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0



use OpenTelemetry\API\Globals;
use OpenTelemetry\API\Trace\Span;
use OpenTelemetry\API\Trace\SpanKind;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Psr\Log\LoggerInterface;
use Slim\App;

return function (App $app) {
    // 🔹 CREATE User
    $app->post('/users', function (Request $request, Response $response, PDO $db, LoggerInterface $logger) {
        $span = Span::getCurrent();
        $span->addEvent('Received create user request');

        $jsonObject = $request->getParsedBody();
        $username = $jsonObject['username'] ?? null;
        $email = $jsonObject['email'] ?? null;
        $password = password_hash($jsonObject['password'] ?? '', PASSWORD_DEFAULT);

        if (!$username || !$email) {
            return respondWithJson($response, ['error' => 'Username and Email are required'], 400);
        }

        $userId = createUser($db, $username, $email, $password);
        $span->addEvent('User created', ['id' => $userId]);
        $logger->info('User created', ['id' => $userId]);

        return respondWithJson($response, ['message' => 'User created successfully', 'id' => $userId]);
    });

    // 🔹 READ All Users
    $app->get('/users', function (Request $request, Response $response, PDO $db, LoggerInterface $logger) {
        $tracer = Globals::tracerProvider()->getTracer('user-service');
        $span = $tracer->spanBuilder('getUsers API')->setSpanKind(SpanKind::KIND_SERVER)->startSpan();

        $span->addEvent('Fetching all users');

        $users = getAllUsers($db);
        $span->addEvent('Users fetched', ['count' => count($users)]);
        $logger->info('Fetched users', ['count' => count($users)]);

        return respondWithJson($response, $users);
    });

    // 🔹 READ Single User
    $app->get('/users/{id}', function (Request $request, Response $response, PDO $db, LoggerInterface $logger) {
        $span = Span::getCurrent();
        $id = (int) $request->getAttribute('id');
        $span->addEvent("Fetching user with ID: $id");

        $user = getUserById($db, $id);
        if (!$user) {
            return respondWithJson($response, ['error' => 'User not found'], 404);
        }

        $span->addEvent('User fetched', ['id' => $id]);
        $logger->info('Fetched user', ['id' => $id]);

        return respondWithJson($response, $user);
    });

    // 🔹 UPDATE User
    $app->put('/users/{id}', function (Request $request, Response $response, PDO $db, LoggerInterface $logger) {
        $span = Span::getCurrent();
        $id = (int) $request->getAttribute('id');
        $jsonObject = $request->getParsedBody();
        $username = $jsonObject['username'] ?? null;
        $email = $jsonObject['email'] ?? null;

        if (!$username || !$email) {
            return respondWithJson($response, ['error' => 'Username and Email are required'], 400);
        }

        $updated = updateUser($db, $id, $username, $email);
        if (!$updated) {
            return respondWithJson($response, ['error' => 'User not found'], 404);
        }

        $span->addEvent('User updated', ['id' => $id]);
        $logger->info('User updated', ['id' => $id]);

        return respondWithJson($response, ['message' => 'User updated successfully']);
    });

    // 🔹 DELETE User
    $app->delete('/users/{id}', function (Request $request, Response $response, PDO $db, LoggerInterface $logger) {
        $span = Span::getCurrent();
        $id = (int) $request->getAttribute('id');

        $deleted = deleteUser($db, $id);
        if (!$deleted) {
            return respondWithJson($response, ['error' => 'User not found'], 404);
        }

        $span->addEvent('User deleted', ['id' => $id]);
        $logger->info('User deleted', ['id' => $id]);

        return respondWithJson($response, ['message' => 'User deleted successfully']);
    });
};

/**
 * 🔹 Helper Function: Create a User with Tracing (Includes SQL Query)
 */
function createUser(PDO $db, string $username, string $email, string $password): int {
    $tracer = Globals::tracerProvider()->getTracer('user-service');
    $span = $tracer->spanBuilder('createUser')->startSpan();
    $span->setAttribute('db.system', 'mysql');
    $span->setAttribute('db.operation', 'INSERT');
    $span->setAttribute('db.table', 'users');

    $sql = "INSERT INTO users (username, email, password) VALUES (:username, :email, :password)";
    $params = ['username' => $username, 'email' => $email];

    // Add SQL query (without sensitive data)
    $span->setAttribute('db.statement', $sql);
    $span->setAttribute('db.parameters', json_encode($params));

    try {
        $stmt = $db->prepare($sql);
        $stmt->execute([...$params, 'password' => $password]);
        $userId = (int) $db->lastInsertId();

        $span->setAttribute('db.user_id', $userId);
        $span->addEvent('User inserted into database');

        return $userId;
    } catch (Throwable $e) {
        $span->recordException($e);
        throw $e;
    } finally {
        $span->end();
    }
}

/**
 * 🔹 Helper Function: Get All Users with Query Info
 */
function getAllUsers(PDO $db): array {
    $tracer = Globals::tracerProvider()->getTracer('user-service');
    $span = $tracer->spanBuilder('getAllUsers')->startSpan();
    $span->setAttribute('db.system', 'mysql');
    $span->setAttribute('db.operation', 'SELECT');
    $span->setAttribute('db.table', 'users');

    $sql = "SELECT id, username, email, created_at FROM users";
    
    // Add query details
    $span->setAttribute('db.statement', $sql);

    try {
        $stmt = $db->query($sql);
        $users = $stmt->fetchAll(PDO::FETCH_ASSOC);

        $span->setAttribute('db.user_count', count($users));
        $span->addEvent('Fetched all users');

        return $users;
    } catch (Throwable $e) {
        $span->recordException($e);
        throw $e;
    } finally {
        $span->end();
    }
}

/**
 * 🔹 Helper Function: Get a User by ID with Query Info
 */
function getUserById(PDO $db, int $id): ?array {
    $tracer = Globals::tracerProvider()->getTracer('user-service');
    $span = $tracer->spanBuilder('getUserById')->startSpan();
    $span->setAttribute('db.system', 'mysql');
    $span->setAttribute('db.operation', 'SELECT');
    $span->setAttribute('db.table', 'users');
    $span->setAttribute('db.user_id', $id);

    $sql = "SELECT id, username, email, created_at FROM users WHERE id = :id";
    $params = ['id' => $id];

    // Add query details
    $span->setAttribute('db.statement', $sql);
    $span->setAttribute('db.parameters', json_encode($params));

    try {
        $stmt = $db->prepare($sql);
        $stmt->execute($params);
        $user = $stmt->fetch(PDO::FETCH_ASSOC);

        if ($user) {
            $span->addEvent('User retrieved');
            return $user;
        }

        $span->addEvent('User not found');
        return null;
    } catch (Throwable $e) {
        $span->recordException($e);
        throw $e;
    } finally {
        $span->end();
    }
}

/**
 * 🔹 Helper Function: Update a User with Query Info
 */
function updateUser(PDO $db, int $id, string $username, string $email): bool {
    $tracer = Globals::tracerProvider()->getTracer('user-service');
    $span = $tracer->spanBuilder('updateUser')->startSpan();
    $span->setAttribute('db.system', 'mysql');
    $span->setAttribute('db.operation', 'UPDATE');
    $span->setAttribute('db.table', 'users');
    $span->setAttribute('db.user_id', $id);

    $sql = "UPDATE users SET username = :username, email = :email WHERE id = :id";
    $params = ['id' => $id, 'username' => $username, 'email' => $email];

    // Add query details
    $span->setAttribute('db.statement', $sql);
    $span->setAttribute('db.parameters', json_encode($params));

    try {
        $stmt = $db->prepare($sql);
        $stmt->execute($params);
        $updated = $stmt->rowCount() > 0;

        if ($updated) {
            $span->addEvent('User updated');
        } else {
            $span->addEvent('User not found');
        }

        return $updated;
    } catch (Throwable $e) {
        $span->recordException($e);
        throw $e;
    } finally {
        $span->end();
    }
}

/**
 * 🔹 Helper Function: Delete a User with Query Info
 */
function deleteUser(PDO $db, int $id): bool {
    $tracer = Globals::tracerProvider()->getTracer('user-service');
    $span = $tracer->spanBuilder('deleteUser')->startSpan();
    $span->setAttribute('db.system', 'mysql');
    $span->setAttribute('db.operation', 'DELETE');
    $span->setAttribute('db.table', 'users');
    $span->setAttribute('db.user_id', $id);

    $sql = "DELETE FROM users WHERE id = :id";
    $params = ['id' => $id];

    // Add query details
    $span->setAttribute('db.statement', $sql);
    $span->setAttribute('db.parameters', json_encode($params));

    try {
        $stmt = $db->prepare($sql);
        $stmt->execute($params);
        $deleted = $stmt->rowCount() > 0;

        if ($deleted) {
            $span->addEvent('User deleted');
        } else {
            $span->addEvent('User not found');
        }

        return $deleted;
    } catch (Throwable $e) {
        $span->recordException($e);
        throw $e;
    } finally {
        $span->end();
    }
}


/**
 * 🔹 Helper Function: JSON Response
 */
function respondWithJson(Response $response, array $data, int $status = 200): Response {
    $response->getBody()->write(json_encode($data));
    return $response->withHeader('Content-Type', 'application/json')->withStatus($status);
}