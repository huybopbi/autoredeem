<?php
/**
 * Helper Functions for CyborX Redeem Tool
 */

/**
 * Generate CSRF token
 */
function generateCsrfToken(): string {
    if (!isset($_SESSION[CSRF_TOKEN_NAME])) {
        $_SESSION[CSRF_TOKEN_NAME] = bin2hex(random_bytes(32));
    }
    return $_SESSION[CSRF_TOKEN_NAME];
}

/**
 * Verify CSRF token
 */
function verifyCsrfToken(string $token): bool {
    return isset($_SESSION[CSRF_TOKEN_NAME]) && hash_equals($_SESSION[CSRF_TOKEN_NAME], $token);
}

/**
 * Generate unique user ID for session
 */
function getUserId(): string {
    if (!isset($_SESSION['user_id'])) {
        $_SESSION['user_id'] = uniqid('user_', true);
    }
    return $_SESSION['user_id'];
}

/**
 * Send JSON response
 */
function jsonResponse(array $data, int $statusCode = 200): void {
    http_response_code($statusCode);
    header('Content-Type: application/json');
    echo json_encode($data);
    exit;
}

/**
 * Send error response
 */
function errorResponse(string $message, int $statusCode = 400): void {
    jsonResponse(['error' => $message], $statusCode);
}

/**
 * Send success response
 */
function successResponse(array $data = []): void {
    jsonResponse(array_merge(['success' => true], $data));
}

/**
 * Parse codes from text
 */
function parseCodesFromText(string $text): array {
    if (empty(trim($text))) {
        return [];
    }
    
    $codes = [];
    $lines = explode("\n", $text);
    
    foreach ($lines as $line) {
        $line = trim($line);
        if (!empty($line) && strpos($line, '#') !== 0) {
            $codes[] = $line;
        }
    }
    
    return $codes;
}

/**
 * Parse cookies from text
 */
function parseCookiesFromText(string $text): array {
    if (empty(trim($text))) {
        return [];
    }
    
    $cookies = [];
    $lines = explode("\n", $text);
    
    foreach ($lines as $line) {
        $line = trim($line);
        if (empty($line) || strpos($line, '#') === 0) {
            continue;
        }
        
        $parts = explode(';', $line);
        foreach ($parts as $part) {
            $part = trim($part);
            if (strpos($part, '=') !== false) {
                $nameValue = explode('=', $part, 2);
                $name = trim($nameValue[0]);
                $value = trim($nameValue[1]);
                $cookies[$name] = $value;
            }
        }
    }
    
    return $cookies;
}

/**
 * Mask sensitive cookie values for display
 */
function maskCookies(array $cookies): array {
    $masked = [];
    foreach ($cookies as $name => $value) {
        if (strlen($value) > 10) {
            $masked[$name] = substr($value, 0, 6) . '...' . substr($value, -4);
        } else {
            $masked[$name] = '***';
        }
    }
    return $masked;
}

/**
 * Render template with variables
 */
function renderTemplate(string $template, array $variables = []): string {
    $templatePath = TEMPLATES_PATH . '/' . $template;
    
    if (!file_exists($templatePath)) {
        throw new Exception("Template not found: $template");
    }
    
    // Extract variables to local scope
    extract($variables);
    
    // Start output buffering
    ob_start();
    
    // Include template
    include $templatePath;
    
    // Get content and clean buffer
    $content = ob_get_clean();
    
    return $content;
}

/**
 * Get current timestamp for logging
 */
function getCurrentTimestamp(): string {
    return date('Y-m-d H:i:s');
}

/**
 * Log message to console (for debugging)
 */
function logMessage(string $message, string $level = 'INFO'): void {
    if (APP_DEBUG) {
        $timestamp = getCurrentTimestamp();
        echo "[$timestamp] [$level] $message\n";
    }
}

/**
 * Validate uploaded file
 */
function validateUploadedFile(array $file): bool {
    return isset($file['tmp_name']) && 
           is_uploaded_file($file['tmp_name']) && 
           $file['error'] === UPLOAD_ERR_OK &&
           $file['size'] <= MAX_FILE_SIZE;
}

/**
 * Get user session data
 */
function getUserSession(): array {
    $userId = getUserId();
    
    if (!isset($_SESSION['user_data'])) {
        $_SESSION['user_data'] = [
            'task_results' => [],
            'task_status' => [
                'running' => false,
                'progress' => 0,
                'total' => 0,
                'success' => 0,
                'error' => 0,
                'current_code' => '',
                'start_time' => null,
                'end_time' => null
            ],
            'data' => [
                'codes' => [],
                'cookies' => [],
                'codes_text' => '',
                'cookies_text' => ''
            ],
            'created_at' => getCurrentTimestamp(),
            'last_accessed' => getCurrentTimestamp()
        ];
    }
    
    // Update last accessed time
    $_SESSION['user_data']['last_accessed'] = getCurrentTimestamp();
    
    return $_SESSION['user_data'];
}

/**
 * Save user session data
 */
function saveUserSession(array $data): void {
    $_SESSION['user_data'] = $data;
}

/**
 * Check if request is AJAX
 */
function isAjaxRequest(): bool {
    return isset($_SERVER['HTTP_X_REQUESTED_WITH']) && 
           strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) === 'xmlhttprequest';
}

/**
 * Get request method
 */
function getRequestMethod(): string {
    return $_SERVER['REQUEST_METHOD'] ?? 'GET';
}

/**
 * Get request URI without query string
 */
function getRequestUri(): string {
    $uri = $_SERVER['REQUEST_URI'] ?? '/';
    return strtok($uri, '?');
}