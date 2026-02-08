// Currently bugged as Mega.nz & Google Drive links are not captured.
// Only dropbox links are currently being grabbed. 
// Planned to be fixed inevitably.

// ==UserScript==
// @name         Kemono Link Auto Copier
// @namespace    https://kemono.cr/
// @version      1.0
// @description  Automatically detects Mega, Google Drive, and Dropbox links on Kemono and copies them to clipboard
// @match        https://kemono.cr/*
// @grant        GM_setClipboard
// ==/UserScript==

(function () {
    'use strict';

    const copiedLinks = new Set();

    const linkPatterns = [
        /https?:\/\/mega\.nz\/[^\s"'<>]+/gi,
        /https?:\/\/drive\.google\.com\/[^\s"'<>]+/gi,
        /https?:\/\/www\.dropbox\.com\/[^\s"'<>]+/gi
    ];

    function scanAndCopy() {
        const bodyText = document.body.innerHTML;

        linkPatterns.forEach(pattern => {
            const matches = bodyText.match(pattern);
            if (!matches) return;

            matches.forEach(link => {
                if (!copiedLinks.has(link)) {
                    copiedLinks.add(link);
                    GM_setClipboard(link);
                    console.log('[Kemono Auto Copy] Copied:', link);
                }
            });
        });
    }

    // Initial scan
    scanAndCopy();

    // Watch for dynamically loaded content
    const observer = new MutationObserver(() => {
        scanAndCopy();
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
})();

