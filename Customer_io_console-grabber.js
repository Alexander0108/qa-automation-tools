
// --------------Тестовий JavaScript Grabber для DevTools у customer (Cmd + Option + J)-------------------


(function() {
    console.log("🛠 Запускаю глибокий пошук...");

    // 1. Функція для пошуку тексту в професійних редакторах
    const getEditorText = () => {
        // Шукаємо Monaco (як у VS Code)
        if (window.monaco && monaco.editor) {
            const editors = monaco.editor.getModels();
            if (editors.length > 0) return editors[0].getValue();
        }
        // Шукаємо Ace Editor
        const aceEl = document.querySelector('.ace_editor');
        if (aceEl && aceEl.env && aceEl.env.editor) {
            return aceEl.env.editor.getValue();
        }
        // Шукаємо просто великі текстові області
        return document.querySelector('textarea.section-html-editor')?.value || 
               document.querySelector('.ace_content')?.innerText || 
               "BODY NOT FOUND";
    };

    // 2. Функція для пошуку Subject та Preheader
    const getField = (label) => {
        const labels = Array.from(document.querySelectorAll('label'));
        const targetLabel = labels.find(el => el.innerText.toLowerCase().includes(label.toLowerCase()));
        if (targetLabel) {
            const input = targetLabel.parentElement.querySelector('input') || targetLabel.parentElement.querySelector('textarea');
            if (input) return input.value;
        }
        // Запасний варіант: пошук за id або класом
        return document.querySelector(`[id*="${label.toLowerCase()}"]`)?.value || "NOT FOUND";
    };

    const subject = getField('subject');
    const preheader = getField('preheader');
    const body = getEditorText();

    const result = `---CIO_DATA_START---\nSUBJECT: ${subject}\nPREHEADER: ${preheader}\nHTML_BODY:\n${body}\n---CIO_DATA_END---`;
    
    copy(result);
    console.log("✅ Результат скопійовано!");
    console.log("📦 Перевір вміст, вставивши його в Нотатки.");
})();