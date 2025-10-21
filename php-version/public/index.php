<?php
/**
 * CyborX Redeem Tool - PHP Version
 * Main entry point
 */

// Load configuration
require_once dirname(__DIR__) . '/config/config.php';

use CyborX\CyborXRedeemTool;

// Initialize global session data
if (!isset($_SESSION['global_task_data'])) {
    $_SESSION['global_task_data'] = [];
}

// Simple routing
$uri = getRequestUri();
$method = getRequestMethod();

// Remove base path if app is in subdirectory
$basePath = rtrim(dirname($_SERVER['SCRIPT_NAME']), '/');
if ($basePath && strpos($uri, $basePath) === 0) {
    $uri = substr($uri, strlen($basePath));
}

// Routes
switch ($uri) {
    case '/':
        if ($method === 'GET') {
            handleHomePage();
        }
        break;
        
    case '/ping':
        if ($method === 'GET') {
            echo 'pong';
            http_response_code(200);
        }
        break;
        
    case '/upload':
        if ($method === 'POST') {
            handleUpload();
        }
        break;
        
    case '/start':
        if ($method === 'POST') {
            handleStart();
        }
        break;
        
    case '/status':
        if ($method === 'GET') {
            handleStatus();
        }
        break;
        
    case '/results':
        if ($method === 'GET') {
            handleResults();
        }
        break;
        
    case '/codes':
        if ($method === 'GET') {
            handleCodes();
        }
        break;
        
    case '/cookies':
        if ($method === 'GET') {
            handleCookies();
        }
        break;
        
    case '/account-info':
        if ($method === 'POST') {
            handleAccountInfo();
        }
        break;
        
    case '/stop':
        if ($method === 'POST') {
            handleStop();
        }
        break;
        
    case '/clear':
        if ($method === 'POST') {
            handleClear();
        }
        break;
        
    case '/cleanup':
        if ($method === 'POST') {
            handleCleanup();
        }
        break;
        
    case '/health':
        if ($method === 'GET') {
            handleHealth();
        }
        break;
        
    default:
        http_response_code(404);
        if (isAjaxRequest()) {
            errorResponse('Endpoint not found', 404);
        } else {
            echo '404 - Page Not Found';
        }
        break;
}

/**
 * Route Handlers
 */

function handleHomePage(): void
{
    try {
        $csrfToken = generateCsrfToken();
        echo renderTemplate('index.html', [
            'csrf_token' => $csrfToken,
            'app_name' => APP_NAME,
            'app_version' => APP_VERSION,
            'base_url' => BASE_URL,
            'assets_url' => ASSETS_URL
        ]);
    } catch (Exception $e) {
        http_response_code(500);
        echo 'Error loading page: ' . $e->getMessage();
    }
}

function handleUpload(): void
{
    try {
        $userSession = getUserSession();
        $userId = getUserId();
        
        // Handle file uploads
        if (isset($_FILES['codes_file']) && validateUploadedFile($_FILES['codes_file'])) {
            $codesText = file_get_contents($_FILES['codes_file']['tmp_name']);
            $codes = parseCodesFromText($codesText);
            $userSession['data']['codes'] = $codes;
            $userSession['data']['codes_text'] = $codesText;
            saveUserSession($userSession);
        }
        
        if (isset($_FILES['cookies_file']) && validateUploadedFile($_FILES['cookies_file'])) {
            $cookiesText = file_get_contents($_FILES['cookies_file']['tmp_name']);
            $cookies = parseCookiesFromText($cookiesText);
            $userSession['data']['cookies'] = $cookies;
            $userSession['data']['cookies_text'] = $cookiesText;
            saveUserSession($userSession);
        }
        
        // Handle manual text input
        if (isset($_POST['codes_text']) && !empty($_POST['codes_text'])) {
            $codesText = $_POST['codes_text'];
            $codes = parseCodesFromText($codesText);
            $userSession['data']['codes'] = $codes;
            $userSession['data']['codes_text'] = $codesText;
            saveUserSession($userSession);
        }
        
        if (isset($_POST['cookies_text']) && !empty($_POST['cookies_text'])) {
            $cookiesText = $_POST['cookies_text'];
            $cookies = parseCookiesFromText($cookiesText);
            $userSession['data']['cookies'] = $cookies;
            $userSession['data']['cookies_text'] = $cookiesText;
            saveUserSession($userSession);
        }
        
        successResponse();
        
    } catch (Exception $e) {
        errorResponse('Error uploading files: ' . $e->getMessage(), 500);
    }
}

function handleStart(): void
{
    try {
        $userSession = getUserSession();
        $userId = getUserId();
        
        // Check if task is already running
        if ($userSession['task_status']['running']) {
            errorResponse('Task is already running', 400);
            return;
        }
        
        // Get codes and cookies
        $codes = $userSession['data']['codes'];
        if (empty($codes)) {
            errorResponse('No codes found. Please upload codes first.', 400);
            return;
        }
        
        $cookies = $userSession['data']['cookies'];
        if (empty($cookies)) {
            errorResponse('No cookies found. Please upload cookies first.', 400);
            return;
        }
        
        // Get input data
        $input = json_decode(file_get_contents('php://input'), true);
        $mode = $input['mode'] ?? 'single';
        
        // Initialize global task data
        $_SESSION['global_task_data'][$userId] = [
            'task_results' => [],
            'task_status' => [
                'running' => true,
                'progress' => 0,
                'total' => count($codes),
                'success' => 0,
                'error' => 0,
                'current_code' => '',
                'start_time' => date('H:i:s'),
                'end_time' => null
            ]
        ];
        
        // Start background process (simplified for demo)
        // In production, you'd use a job queue or background processor
        startRedeemProcess($codes, $cookies, $userId);
        
        successResponse(['message' => 'Redeem process started successfully!']);
        
    } catch (Exception $e) {
        errorResponse('Start redeem failed: ' . $e->getMessage(), 500);
    }
}

function startRedeemProcess(array $codes, array $cookies, string $userId): void
{
    // For demo purposes, we'll run a few codes synchronously
    // In production, this should be run in background
    $tool = new CyborXRedeemTool($cookies, $userId);
    
    // Run first few codes only (to avoid timeout)
    $limitedCodes = array_slice($codes, 0, min(3, count($codes)));
    $tool->runSingleThread($limitedCodes);
}

function handleStatus(): void
{
    $userId = getUserId();
    
    if (isset($_SESSION['global_task_data'][$userId])) {
        jsonResponse($_SESSION['global_task_data'][$userId]['task_status']);
    } else {
        jsonResponse([
            'running' => false,
            'progress' => 0,
            'total' => 0,
            'success' => 0,
            'error' => 0,
            'current_code' => '',
            'start_time' => null,
            'end_time' => null
        ]);
    }
}

function handleResults(): void
{
    $userId = getUserId();
    
    if (isset($_SESSION['global_task_data'][$userId])) {
        jsonResponse($_SESSION['global_task_data'][$userId]['task_results']);
    } else {
        jsonResponse([]);
    }
}

function handleCodes(): void
{
    try {
        $userSession = getUserSession();
        $codes = $userSession['data']['codes'];
        
        jsonResponse([
            'codes' => $codes,
            'count' => count($codes),
            'filename' => count($codes) > 0 ? 'Session Data' : 'No data'
        ]);
    } catch (Exception $e) {
        errorResponse($e->getMessage(), 500);
    }
}

function handleCookies(): void
{
    try {
        $userSession = getUserSession();
        $cookies = $userSession['data']['cookies'];
        $maskedCookies = maskCookies($cookies);
        
        jsonResponse([
            'cookies' => $maskedCookies,
            'count' => count($cookies),
            'filename' => count($cookies) > 0 ? 'Session Data' : 'No data'
        ]);
    } catch (Exception $e) {
        errorResponse($e->getMessage(), 500);
    }
}

function handleAccountInfo(): void
{
    try {
        $input = json_decode(file_get_contents('php://input'), true);
        
        if (!$input || empty($input['cookies_text'])) {
            errorResponse('No cookies provided', 400);
            return;
        }
        
        $cookiesText = $input['cookies_text'];
        $cookies = parseCookiesFromText($cookiesText);
        
        if (empty($cookies)) {
            errorResponse('Invalid cookies format', 400);
            return;
        }
        
        $tool = new CyborXRedeemTool($cookies);
        $accountInfo = $tool->getAccountInfo();
        
        jsonResponse($accountInfo);
        
    } catch (Exception $e) {
        errorResponse($e->getMessage(), 500);
    }
}

function handleStop(): void
{
    $userSession = getUserSession();
    
    if (!$userSession['task_status']['running']) {
        errorResponse('No task is running', 400);
        return;
    }
    
    $userSession['task_status']['running'] = false;
    $userSession['task_status']['end_time'] = date('H:i:s');
    saveUserSession($userSession);
    
    // Also update global task data
    $userId = getUserId();
    if (isset($_SESSION['global_task_data'][$userId])) {
        $_SESSION['global_task_data'][$userId]['task_status']['running'] = false;
        $_SESSION['global_task_data'][$userId]['task_status']['end_time'] = date('H:i:s');
    }
    
    successResponse(['message' => 'Stop signal sent']);
}

function handleClear(): void
{
    $userSession = getUserSession();
    
    $userSession['task_results'] = [];
    $userSession['task_status'] = [
        'running' => false,
        'progress' => 0,
        'total' => 0,
        'success' => 0,
        'error' => 0,
        'current_code' => '',
        'start_time' => null,
        'end_time' => null
    ];
    
    saveUserSession($userSession);
    
    // Clear global task data
    $userId = getUserId();
    if (isset($_SESSION['global_task_data'][$userId])) {
        unset($_SESSION['global_task_data'][$userId]);
    }
    
    successResponse(['message' => 'Results cleared']);
}

function handleCleanup(): void
{
    try {
        // Clear all session data
        session_unset();
        session_destroy();
        
        // Start new session
        session_start();
        
        successResponse(['message' => 'Session cleaned up successfully!']);
        
    } catch (Exception $e) {
        errorResponse($e->getMessage(), 500);
    }
}

function handleHealth(): void
{
    try {
        $healthInfo = [
            'status' => 'healthy',
            'app' => 'running',
            'timestamp' => getCurrentTimestamp(),
            'php_version' => PHP_VERSION,
            'extensions' => [
                'curl' => extension_loaded('curl'),
                'json' => extension_loaded('json'),
                'session' => extension_loaded('session'),
                'mbstring' => extension_loaded('mbstring')
            ]
        ];
        
        jsonResponse($healthInfo);
        
    } catch (Exception $e) {
        $errorInfo = [
            'status' => 'unhealthy',
            'app' => 'error',
            'error' => $e->getMessage(),
            'timestamp' => getCurrentTimestamp()
        ];
        
        jsonResponse($errorInfo, 503);
    }
}