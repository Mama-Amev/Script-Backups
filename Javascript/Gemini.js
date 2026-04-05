// ==UserScript==
// @name         Gemini Redo on Left Ctrl (Debug)
// @namespace    http://tampermonkey.net/
// @version      1.2
// @description  Press Left Ctrl to click the Redo button on the latest Gemini prompt
// @author       You
// @match        https://gemini.google.com/*
// @grant        none
// @run-at       document-start
// ==/UserScript==

(function () {
  'use strict';

  console.log('[Gemini Redo] ✅ Script loaded and running.');

  function clickLastRedoButton() {
    console.log('[Gemini Redo] Searching for Redo button...');

    // Log ALL buttons on the page so we can see what Gemini actually calls it
    const allButtons = Array.from(document.querySelectorAll('button'));
    console.log(`[Gemini Redo] Total buttons found: ${allButtons.length}`);
    allButtons.forEach((btn, i) => {
      const label = btn.getAttribute('aria-label') || '';
      const title = btn.getAttribute('title') || '';
      const mat   = btn.getAttribute('mattooltip') || '';
      const text  = (btn.innerText || '').trim().substring(0, 40);
      if (label || title || mat || text) {
        console.log(`[Gemini Redo] Button ${i}: aria-label="${label}" title="${title}" mattooltip="${mat}" text="${text}"`);
      }
    });

    // Try every reasonable selector
    const selectors = [
      'button[aria-label="Redo"]',
      'button[aria-label="redo"]',
      'button[title="Redo"]',
      'button[title="redo"]',
      'button[data-tooltip="Redo"]',
      'button[mattooltip="Redo"]',
    ];

    let redoButtons = [];
    for (const selector of selectors) {
      const found = Array.from(document.querySelectorAll(selector));
      if (found.length > 0) {
        console.log(`[Gemini Redo] Found via selector: ${selector}`);
        redoButtons = found;
        break;
      }
    }

    // Broad text fallback
    if (redoButtons.length === 0) {
      redoButtons = allButtons.filter(btn => {
        const label = (btn.getAttribute('aria-label') || '').toLowerCase();
        const title = (btn.getAttribute('title') || '').toLowerCase();
        const mat   = (btn.getAttribute('mattooltip') || '').toLowerCase();
        const text  = (btn.innerText || '').toLowerCase().trim();
        return label.includes('redo') || title.includes('redo') || mat.includes('redo') || text === 'redo';
      });
      console.log(`[Gemini Redo] Broad fallback found ${redoButtons.length} button(s).`);
    }

    if (redoButtons.length === 0) {
      console.warn('[Gemini Redo] ❌ No Redo button found. Check the button list above for clues.');
      return;
    }

    const target = redoButtons[redoButtons.length - 1];
    console.log('[Gemini Redo] Clicking target:', target);

    target.style.visibility = 'visible';
    target.style.opacity = '1';
    target.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
    console.log('[Gemini Redo] ✅ Click dispatched.');
  }

  let lastFired = 0;

  // Try both window and document listeners
  const handler = function (e) {
    console.log(`[Gemini Redo] Key detected: ${e.code}, ctrl=${e.ctrlKey}`);
    if (e.code === 'ControlLeft') {
      const now = Date.now();
      if (now - lastFired < 500) return;
      lastFired = now;
      if (e.altKey || e.shiftKey || e.metaKey) return;
      e.preventDefault();
      e.stopPropagation();
      clickLastRedoButton();
    }
  };

  document.addEventListener('keydown', handler, true);
  window.addEventListener('keydown', handler, true);

})();
