import React, { useState } from 'react';
import axios from 'axios';
import { Languages, Upload, Image as ImageIcon, Loader2 } from 'lucide-react';

const LANGUAGES = [
  { code: 'en', name: 'English' },
  { code: 'zh-TW', name: 'Traditional Chinese' },
  { code: 'zh-CN', name: 'Simplified Chinese' },
  { code: 'ja', name: 'Japanese' },
  { code: 'ko', name: 'Korean' },
  { code: 'de', name: 'German' },
  { code: 'fr', name: 'French' },
  { code: 'es', name: 'Spanish' },
];

function App() {
  const [inputText, setInputText] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [sourceLang, setSourceLang] = useState('en');
  const [targetLang, setTargetLang] = useState('zh-TW');
  const [loading, setLoading] = useState(false);
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  const handleTranslateText = async () => {
    if (!inputText) return;
    setLoading(true);
    try {
      const response = await axios.post('/api/translate', {
        text: inputText,
        source_lang: sourceLang,
        target_lang: targetLang,
      });
      setTranslatedText(response.data.translated_text);
    } catch (error) {
      console.error('Translation error:', error);
      alert('Translation failed. Please check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleTranslateImage = async () => {
    if (!image) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', image);
    formData.append('source_lang', sourceLang);
    formData.append('target_lang', targetLang);

    try {
      const response = await axios.post('/api/translate-image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setTranslatedText(response.data.translated_text);
    } catch (error) {
      console.error('Image translation error:', error);
      alert('Image translation failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container py-5">
      <header className="text-center mb-5">
        <h1 className="display-4 d-flex align-items-center justify-content-center">
          <Languages className="me-3 text-primary" size={48} />
          Open Translate
        </h1>
        <p className="lead text-muted">Powered by Google TranslateGemma</p>
      </header>

      <div className="row g-4">
        {/* Language Selection */}
        <div className="col-12">
          <div className="card shadow-sm">
            <div className="card-body d-flex justify-content-between align-items-center">
              <select 
                className="form-select w-auto" 
                value={sourceLang} 
                onChange={(e) => setSourceLang(e.target.value)}
              >
                {LANGUAGES.map(l => <option key={l.code} value={l.code}>{l.name}</option>)}
              </select>
              <div className="mx-3 text-muted">to</div>
              <select 
                className="form-select w-auto" 
                value={targetLang} 
                onChange={(e) => setTargetLang(e.target.value)}
              >
                {LANGUAGES.map(l => <option key={l.code} value={l.code}>{l.name}</option>)}
              </select>
            </div>
          </div>
        </div>

        {/* Text Input Area */}
        <div className="col-md-6">
          <div className="card shadow-sm h-100">
            <div className="card-header bg-white">
              <h5 className="mb-0">Source Text</h5>
            </div>
            <div className="card-body">
              <textarea
                className="form-control border-0"
                rows="10"
                placeholder="Enter text here..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                style={{ resize: 'none' }}
              ></textarea>
              <div className="mt-3 d-flex justify-content-between align-items-center">
                <div className="input-group w-auto">
                  <input type="file" className="d-none" id="imgUpload" onChange={handleImageChange} accept="image/*" />
                  <label className="btn btn-outline-secondary" htmlFor="imgUpload">
                    <ImageIcon className="me-2" size={18} />
                    Upload Image
                  </label>
                </div>
                <button 
                  className="btn btn-primary px-4" 
                  onClick={handleTranslateText}
                  disabled={loading || !inputText}
                >
                  {loading ? <Loader2 className="spinner-border spinner-border-sm" /> : 'Translate'}
                </button>
              </div>
              {imagePreview && (
                <div className="mt-3 text-center border rounded p-2">
                  <img src={imagePreview} alt="Preview" className="img-fluid mb-2" style={{ maxHeight: '150px' }} />
                  <br />
                  <button className="btn btn-sm btn-info" onClick={handleTranslateImage} disabled={loading}>
                    Translate Image
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Translation Output Area */}
        <div className="col-md-6">
          <div className="card shadow-sm h-100 bg-white">
            <div className="card-header bg-white">
              <h5 className="mb-0">Translation</h5>
            </div>
            <div className="card-body">
              <div className="h-100 p-2 text-dark" style={{ minHeight: '240px', whiteSpace: 'pre-wrap' }}>
                {translatedText || <span className="text-muted">Translation will appear here...</span>}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
