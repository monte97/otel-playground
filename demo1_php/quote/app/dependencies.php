<?php
// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0



declare(strict_types=1);

use App\Application\Settings\SettingsInterface;
use DI\ContainerBuilder;
use OpenTelemetry\API\Globals;
use OpenTelemetry\Contrib\Logs\Monolog\Handler;
use Monolog\Logger;
use Psr\Container\ContainerInterface;
use Psr\Log\LoggerInterface;
use Psr\Log\LogLevel;

return function (ContainerBuilder $containerBuilder) {
    $containerBuilder->addDefinitions([
        LoggerInterface::class => function (ContainerInterface $c) {
            $settings = $c->get(SettingsInterface::class);
            $loggerSettings = $settings->get('logger');
            $handler = new Handler(
                Globals::loggerProvider(),
                LogLevel::INFO,
            );
            return new Logger($loggerSettings['name'], [$handler]);
        },

        // 🔹 Register PDO in the DI container
        PDO::class => function () {
            $host = 'php-api-db';
            $db = 'mydatabase';
            $user = 'user';
            $pass = 'password';
            $charset = 'utf8mb4';

            $dsn = "mysql:host=$host;dbname=$db;charset=$charset";
            $options = [
                PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES   => false,
            ];

            return new PDO($dsn, $user, $pass, $options);
        },
    ]);
};
