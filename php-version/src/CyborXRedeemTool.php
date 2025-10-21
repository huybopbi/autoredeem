<?php

namespace CyborX;

/**
 * CyborX Redeem Tool - PHP Implementation
 * 
 * Main class for handling code redemption on cyborx.net
 */
class CyborXRedeemTool
{
    private $baseUrl;
    private $redeemUrl;
    private $dashboardUrl;
    private $cookies;
    private $headers;
    
    // Statistics
    private $processedCount = 0;
    private $successCount = 0;
    private $errorCount = 0;
    private $totalCodes = 0;
    private $shouldStop = false;
    
    // Session reference for web updates
    private $sessionData;
    private $userId;
    
    public function __construct(array $cookies = [], ?string $userId = null)
    {
        $this->baseUrl = CYBORX_BASE_URL;
        $this->redeemUrl = CYBORX_REDEEM_URL;
        $this->dashboardUrl = CYBORX_DASHBOARD_URL;
        $this->cookies = $cookies;
        $this->userId = $userId;
        
        // Default headers similar to browser
        $this->headers = [
            'User-Agent: ' . USER_AGENT,
            'Accept: */*',
            'Accept-Language: vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
            'Content-Type: application/x-www-form-urlencoded; charset=UTF-8',
            'Origin: https://cyborx.net',
            'Referer: https://cyborx.net/app/redeem',
            'X-Requested-With: XMLHttpRequest',
            'Sec-Ch-Ua: "Chromium";v="137", "Not/A)Brand";v="24"',
            'Sec-Ch-Ua-Mobile: ?0',
            'Sec-Ch-Ua-Platform: "Windows"',
            'Sec-Fetch-Dest: empty',
            'Sec-Fetch-Mode: cors',
            'Sec-Fetch-Site: same-origin'
        ];
        
        // Set session data reference
        if ($this->userId && isset($_SESSION['global_task_data'][$this->userId])) {
            $this->sessionData = &$_SESSION['global_task_data'][$this->userId];
        }
    }
    
    /**
     * Initialize cURL handle with common settings
     */
    private function initCurl(): \CurlHandle
    {
        $curl = curl_init();
        
        curl_setopt_array($curl, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => REQUEST_TIMEOUT,
            CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_MAXREDIRS => 3,
            CURLOPT_SSL_VERIFYPEER => true,
            CURLOPT_SSL_VERIFYHOST => 2,
            CURLOPT_HTTPHEADER => $this->headers,
            CURLOPT_COOKIEJAR => '', // Enable cookie handling
            CURLOPT_COOKIEFILE => '', // Enable cookie handling
        ]);
        
        // Set cookies if provided
        if (!empty($this->cookies)) {
            $cookieString = '';
            foreach ($this->cookies as $name => $value) {
                $cookieString .= $name . '=' . $value . '; ';
            }
            curl_setopt($curl, CURLOPT_COOKIE, rtrim($cookieString, '; '));
        }
        
        return $curl;
    }
    
    /**
     * Update progress statistics
     */
    private function updateProgress(): void
    {
        $this->processedCount++;
        
        // Update session data if available
        if ($this->sessionData) {
            $this->sessionData['task_status']['progress'] = $this->processedCount;
            $this->sessionData['task_status']['success'] = $this->successCount;
            $this->sessionData['task_status']['error'] = $this->errorCount;
        }
        
        if (APP_DEBUG) {
            $remaining = $this->totalCodes - $this->processedCount;
            logMessage("Progress: {$this->processedCount}/{$this->totalCodes} | Remaining: $remaining");
        }
    }
    
    /**
     * Redeem a single code
     */
    public function redeemCode(string $code, int $codeNumber): ?array
    {
        try {
            $code = trim($code);
            
            if (APP_DEBUG) {
                logMessage("Processing ({$codeNumber}/{$this->totalCodes}): $code");
            }
            
            // Update current code being processed
            if ($this->sessionData) {
                $this->sessionData['task_status']['current_code'] = $code;
            }
            
            $curl = $this->initCurl();
            
            // Prepare POST data
            $postData = http_build_query(['code' => $code]);
            
            curl_setopt_array($curl, [
                CURLOPT_URL => $this->redeemUrl,
                CURLOPT_POST => true,
                CURLOPT_POSTFIELDS => $postData
            ]);
            
            $response = curl_exec($curl);
            $httpCode = curl_getinfo($curl, CURLINFO_HTTP_CODE);
            $error = curl_error($curl);
            
            curl_close($curl);
            
            $this->updateProgress();
            
            if ($error) {
                throw new \Exception("cURL Error: $error");
            }
            
            $result = [
                'code' => $code,
                'status_code' => $httpCode,
                'response' => $response,
                'number' => $codeNumber,
                'timestamp' => getCurrentTimestamp()
            ];
            
            if ($httpCode === 200) {
                $this->processResponse($response, $code, $codeNumber);
            } else {
                if (APP_DEBUG) {
                    logMessage("HTTP Error ({$codeNumber}/{$this->totalCodes}): $code - Status: $httpCode");
                }
                $this->errorCount++;
                $this->addResultToSession($code, 'error', "HTTP Error: $httpCode");
            }
            
            return $result;
            
        } catch (\Exception $e) {
            $this->updateProgress();
            $this->errorCount++;
            
            if (APP_DEBUG) {
                logMessage("Error ({$codeNumber}/{$this->totalCodes}): $code - " . $e->getMessage(), 'ERROR');
            }
            
            $this->addResultToSession($code, 'error', $e->getMessage());
            return null;
        }
    }
    
    /**
     * Process API response
     */
    private function processResponse(string $response, string $code, int $codeNumber): void
    {
        $responseText = trim($response);
        
        // Try to parse JSON response first
        $responseData = json_decode($responseText, true);
        
        if (json_last_error() === JSON_ERROR_NONE && is_array($responseData)) {
            // JSON response
            if (isset($responseData['ok']) && $responseData['ok'] === true) {
                // Success
                $this->successCount++;
                $this->shouldStop = true; // Stop after first success
                
                $data = $responseData['data'] ?? [];
                $creditsAdded = $data['credits_added'] ?? 0;
                $newStatus = $data['new_status'] ?? '';
                $newExpiry = $data['new_expiry'] ?? '';
                
                if (APP_DEBUG) {
                    logMessage("SUCCESS ({$codeNumber}/{$this->totalCodes}): $code");
                    logMessage("Response: $responseText");
                    if ($creditsAdded > 0) logMessage("Credits Added: $creditsAdded");
                    if ($newStatus) logMessage("New Status: $newStatus");
                    if ($newExpiry) logMessage("New Expiry: $newExpiry");
                }
                
                $this->addResultToSession($code, 'success', $responseText);
                
                // Stop the task
                if ($this->sessionData) {
                    $this->sessionData['task_status']['running'] = false;
                    $this->sessionData['task_status']['end_time'] = date('H:i:s');
                }
                
            } else {
                // API returned error
                $errorMsg = $responseData['error'] ?? 'Unknown error';
                $this->errorCount++;
                
                if (APP_DEBUG) {
                    logMessage("API Error ({$codeNumber}/{$this->totalCodes}): $code");
                    logMessage("Response: $responseText");
                    logMessage("Error: $errorMsg");
                }
                
                $this->addResultToSession($code, 'error', $responseText);
            }
        } else {
            // Text response - fallback to keyword detection
            $responseLower = strtolower($responseText);
            
            if (strpos($responseLower, 'success') !== false || strpos($responseLower, 'redeemed') !== false) {
                $this->successCount++;
                $this->shouldStop = true;
                
                if (APP_DEBUG) {
                    logMessage("SUCCESS ({$codeNumber}/{$this->totalCodes}): $code");
                    logMessage("Response: $responseText");
                }
                
                $this->addResultToSession($code, 'success', $responseText);
                
                // Stop the task
                if ($this->sessionData) {
                    $this->sessionData['task_status']['running'] = false;
                    $this->sessionData['task_status']['end_time'] = date('H:i:s');
                }
                
            } elseif (strpos($responseLower, 'not found') !== false) {
                $this->errorCount++;
                
                if (APP_DEBUG) {
                    logMessage("NOT FOUND ({$codeNumber}/{$this->totalCodes}): $code");
                    logMessage("Response: $responseText");
                }
                
                $this->addResultToSession($code, 'error', $responseText);
                
            } elseif (strpos($responseLower, 'already used') !== false || strpos($responseLower, 'expired') !== false) {
                $this->errorCount++;
                
                if (APP_DEBUG) {
                    logMessage("ALREADY USED/EXPIRED ({$codeNumber}/{$this->totalCodes}): $code");
                    logMessage("Response: $responseText");
                }
                
                $this->addResultToSession($code, 'error', $responseText);
                
            } else {
                $this->errorCount++;
                
                if (APP_DEBUG) {
                    logMessage("UNKNOWN ({$codeNumber}/{$this->totalCodes}): $code");
                    logMessage("Response: $responseText");
                }
                
                $this->addResultToSession($code, 'error', $responseText);
            }
        }
    }
    
    /**
     * Add result to session data
     */
    private function addResultToSession(string $code, string $status, string $response): void
    {
        if ($this->sessionData) {
            $this->sessionData['task_results'][] = [
                'code' => $code,
                'status' => $status,
                'response' => $response,
                'timestamp' => date('H:i:s')
            ];
        }
    }
    
    /**
     * Run single-threaded redeem process
     */
    public function runSingleThread(array $codes): void
    {
        $this->totalCodes = count($codes);
        $this->shouldStop = false;
        
        if (APP_DEBUG) {
            logMessage("Loaded {$this->totalCodes} codes");
            logMessage("Mode: Single Thread");
            logMessage("Timeout: " . REQUEST_TIMEOUT . " seconds");
            logMessage("Starting redeem process...");
            logMessage("Will stop after first successful redeem");
        }
        
        foreach ($codes as $index => $code) {
            if ($this->shouldStop) {
                if (APP_DEBUG) {
                    logMessage("Stopping after successful redeem at code " . ($index));
                }
                break;
            }
            
            $this->redeemCode($code, $index + 1);
            
            // Small delay between requests
            usleep(500000); // 0.5 seconds
        }
        
        // Final update
        if ($this->sessionData) {
            $this->sessionData['task_status']['running'] = false;
            if (!$this->sessionData['task_status']['end_time']) {
                $this->sessionData['task_status']['end_time'] = date('H:i:s');
            }
        }
    }
    
    /**
     * Get account information from cyborx.net dashboard
     */
    public function getAccountInfo(): array
    {
        try {
            $curl = $this->initCurl();
            
            curl_setopt_array($curl, [
                CURLOPT_URL => $this->dashboardUrl,
                CURLOPT_HTTPGET => true
            ]);
            
            $response = curl_exec($curl);
            $httpCode = curl_getinfo($curl, CURLINFO_HTTP_CODE);
            $error = curl_error($curl);
            
            curl_close($curl);
            
            if ($error) {
                throw new \Exception("cURL Error: $error");
            }
            
            if ($httpCode !== 200) {
                throw new \Exception("HTTP Error: $httpCode");
            }
            
            // Parse HTML response to extract account info
            return $this->parseAccountInfo($response);
            
        } catch (\Exception $e) {
            return [
                'status' => 'error',
                'error' => $e->getMessage()
            ];
        }
    }
    
    /**
     * Parse account information from dashboard HTML
     */
    private function parseAccountInfo(string $html): array
    {
        $accountInfo = [
            'status' => 'success',
            'account_type' => 'Unknown',
            'expiry_date' => 'Unknown',
            'credits' => 'Unknown',
            'kcoin' => 'Unknown',
            'xcoin' => 'Unknown',
            'username' => 'Unknown'
        ];
        
        // Use DOMDocument for HTML parsing
        $dom = new \DOMDocument();
        @$dom->loadHTML($html);
        $xpath = new \DOMXPath($dom);
        
        // Find username (look for @username pattern)
        $profileLinks = $xpath->query('//a[@href="/app/settings"]');
        if ($profileLinks->length > 0) {
            $profileText = $profileLinks->item(0)->textContent;
            if (preg_match('/@(\w+)/', $profileText, $matches)) {
                $accountInfo['username'] = $matches[1];
            }
            
            if (stripos($profileText, 'PREMIUM') !== false) {
                $accountInfo['account_type'] = 'Premium';
            } else {
                $accountInfo['account_type'] = 'Free';
            }
        }
        
        // Find credits, kcoin, xcoin values
        $this->extractValueByLabel($xpath, 'Credits', $accountInfo, 'credits');
        $this->extractValueByLabel($xpath, 'KCoin', $accountInfo, 'kcoin');
        $this->extractValueByLabel($xpath, 'XCoin', $accountInfo, 'xcoin');
        
        // Find expiry date
        $expiryElements = $xpath->query('//*[text()="Expiry Date"]');
        if ($expiryElements->length > 0) {
            $expiryElement = $expiryElements->item(0);
            $parent = $expiryElement->parentNode;
            
            // Look for date pattern in parent or siblings
            if ($parent) {
                $parentText = $parent->textContent;
                if (preg_match('/(\d{2}\/\d{2}\/\d{4})/', $parentText, $matches)) {
                    $accountInfo['expiry_date'] = $matches[1];
                } else {
                    // Check next sibling or grandparent structure
                    $grandparent = $parent->parentNode;
                    if ($grandparent && $grandparent->nextSibling) {
                        $nextElement = $grandparent->nextSibling;
                        while ($nextElement && $nextElement->nodeType !== XML_ELEMENT_NODE) {
                            $nextElement = $nextElement->nextSibling;
                        }
                        if ($nextElement) {
                            $dateDiv = $xpath->query('.//div[@class="k"]', $nextElement);
                            if ($dateDiv->length > 0) {
                                $dateText = $dateDiv->item(0)->textContent;
                                if (preg_match('/(\d{2}\/\d{2}\/\d{4})/', $dateText, $matches)) {
                                    $accountInfo['expiry_date'] = $matches[1];
                                }
                            }
                        }
                    }
                }
            }
        }
        
        return $accountInfo;
    }
    
    /**
     * Extract value by label from HTML
     */
    private function extractValueByLabel(\DOMXPath $xpath, string $label, array &$accountInfo, string $key): void
    {
        $elements = $xpath->query("//*[text()='$label']");
        if ($elements->length > 0) {
            $element = $elements->item(0);
            $parent = $element->parentNode;
            if ($parent && $parent->nextSibling) {
                $nextSibling = $parent->nextSibling;
                while ($nextSibling && $nextSibling->nodeType !== XML_ELEMENT_NODE) {
                    $nextSibling = $nextSibling->nextSibling;
                }
                if ($nextSibling) {
                    $text = trim($nextSibling->textContent);
                    if ($key === 'xcoin') {
                        $text = str_replace('$', '', $text);
                    }
                    if (is_numeric($text)) {
                        $accountInfo[$key] = $text;
                    }
                }
            }
        }
    }
    
    /**
     * Get statistics
     */
    public function getStats(): array
    {
        return [
            'processed' => $this->processedCount,
            'success' => $this->successCount,
            'error' => $this->errorCount,
            'total' => $this->totalCodes,
            'success_rate' => $this->totalCodes > 0 ? round(($this->successCount / $this->totalCodes) * 100, 1) : 0
        ];
    }
    
    /**
     * Print summary (for CLI usage)
     */
    public function printSummary(): void
    {
        $stats = $this->getStats();
        
        echo str_repeat('=', 70) . "\n";
        echo "[SUMMARY] FINAL SUMMARY:\n";
        echo "[OK] Successful: {$stats['success']}/{$stats['total']}\n";
        echo "[FAILED] {$stats['error']}/{$stats['total']}\n";
        echo "[TOTAL] Processed: {$stats['total']}\n";
        echo "[RATE] Success rate: {$stats['success_rate']}%\n";
    }
}