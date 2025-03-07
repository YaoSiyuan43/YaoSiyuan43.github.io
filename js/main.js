const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const textInput = document.getElementById('text-input');
const generateBtn = document.getElementById('generate-btn');
const clearBtn = document.getElementById('clear-btn');
const processingModal = document.getElementById('processing-modal');
const resultContainer = document.getElementById('result-container');

function createFloatingChars() {
    const container = document.getElementById('floating-chars');
    const chars = '词云云WordCloud';
    for(let i = 0; i < 20; i++) {
        const char = document.createElement('div');
        char.className = 'absolute text-white text-opacity-20 text-2xl floating-text';
        char.style.left = `${Math.random() * 100}%`;
        char.style.top = `${Math.random() * 100}%`;
        char.style.animationDelay = `${Math.random() * 5}s`;
        char.textContent = chars[Math.floor(Math.random() * chars.length)];
        container.appendChild(char);
    }
}

function showProcessing() {
    processingModal.style.display = 'flex';
}

function hideProcessing() {
    processingModal.style.display = 'none';
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    resultContainer.innerHTML = '';
    resultContainer.appendChild(errorDiv);
}

function displayResults(data) {
    resultContainer.innerHTML = '';
    
    // 显示中文词云
    if (data.chinese && data.chinese.length > 0) {
        const chineseSection = document.createElement('div');
        chineseSection.className = 'result-section';
        chineseSection.innerHTML = '<h3 class="section-title">中文词云</h3>';
        
        const chineseCloud = document.createElement('div');
        chineseCloud.className = 'word-cloud-container';
        data.chinese.slice(0, 50).forEach(([word, freq]) => {
            const wordItem = document.createElement('div');
            wordItem.className = 'word-item';
            wordItem.innerHTML = `${word}<span class="word-frequency">${freq}</span>`;
            chineseCloud.appendChild(wordItem);
        });
        
        chineseSection.appendChild(chineseCloud);
        resultContainer.appendChild(chineseSection);
    }
    
    // 显示英文词云
    if (data.english && data.english.length > 0) {
        const englishSection = document.createElement('div');
        englishSection.className = 'result-section';
        englishSection.innerHTML = '<h3 class="section-title">English Word Cloud</h3>';
        
        const englishCloud = document.createElement('div');
        englishCloud.className = 'word-cloud-container';
        data.english.slice(0, 50).forEach(([word, freq]) => {
            const wordItem = document.createElement('div');
            wordItem.className = 'word-item';
            wordItem.innerHTML = `${word}<span class="word-frequency">${freq}</span>`;
            englishCloud.appendChild(wordItem);
        });
        
        englishSection.appendChild(englishCloud);
        resultContainer.appendChild(englishSection);
    }
}

async function processFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showProcessing();
        const response = await fetch('http://localhost:5000/api/process', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('处理文件时出错');
        }
        
        const data = await response.json();
        displayResults(data);
    } catch (error) {
        showError(error.message);
    } finally {
        hideProcessing();
    }
}

// 事件监听器
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('border-secondary');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('border-secondary');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('border-secondary');
    const file = e.dataTransfer.files[0];
    handleFile(file);
});

fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    handleFile(file);
});

function handleFile(file) {
    if(!file) return;
    processingModal.style.display = 'flex';
    setTimeout(() => {
        processingModal.style.display = 'none';
        textInput.value = `Sample text from ${file.name}`;
    }, 2000);
}

clearBtn.addEventListener('click', () => {
    textInput.value = '';
    fileInput.value = '';
    resultContainer.innerHTML = '';
});

generateBtn.addEventListener('click', () => {
    if(!textInput.value.trim()) return;
    processingModal.style.display = 'flex';
    setTimeout(() => {
        processingModal.style.display = 'none';
    }, 2000);
});

// 初始化
createFloatingChars(); 