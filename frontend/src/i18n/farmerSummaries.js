export const SUMMARY_LANGUAGES = [
  { code: 'en', label: 'English', summaryTitle: 'In simple words', languageLabel: 'Language' },
  { code: 'kn', label: 'ಕನ್ನಡ', summaryTitle: 'ಸರಳವಾಗಿ ಹೇಳುವುದಾದರೆ', languageLabel: 'ಭಾಷೆ', loading: 'ಸಾರಾಂಶವನ್ನು ಅನುವಾದಿಸಲಾಗುತ್ತಿದೆ…', error: 'ಈಗ ಅನುವಾದ ಲಭ್ಯವಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.' },
  { code: 'hi', label: 'हिन्दी', summaryTitle: 'आसान शब्दों में', languageLabel: 'भाषा', loading: 'सार का अनुवाद हो रहा है…', error: 'अभी अनुवाद उपलब्ध नहीं है। कृपया फिर कोशिश करें।' },
  { code: 'pa', label: 'ਪੰਜਾਬੀ', summaryTitle: 'ਸੌਖੇ ਸ਼ਬਦਾਂ ਵਿੱਚ', languageLabel: 'ਭਾਸ਼ਾ', loading: 'ਸੰਖੇਪ ਦਾ ਅਨੁਵਾਦ ਹੋ ਰਿਹਾ ਹੈ…', error: 'ਇਸ ਵੇਲੇ ਅਨੁਵਾਦ ਉਪਲਬਧ ਨਹੀਂ। ਕਿਰਪਾ ਕਰਕੇ ਫਿਰ ਕੋਸ਼ਿਸ਼ ਕਰੋ।' },
  { code: 'gu', label: 'ગુજરાતી', summaryTitle: 'સરળ શબ્દોમાં', languageLabel: 'ભાષા', loading: 'સારાંશનો અનુવાદ થઈ રહ્યો છે…', error: 'હાલ અનુવાદ ઉપલબ્ધ નથી. કૃપા કરીને ફરી પ્રયાસ કરો.' },
  { code: 'mr', label: 'मराठी', summaryTitle: 'सोप्या शब्दांत', languageLabel: 'भाषा', loading: 'सारांशाचा अनुवाद सुरू आहे…', error: 'सध्या अनुवाद उपलब्ध नाही. कृपया पुन्हा प्रयत्न करा.' },
  { code: 'te', label: 'తెలుగు', summaryTitle: 'సరళంగా చెప్పాలంటే', languageLabel: 'భాష', loading: 'సారాంశం అనువదించబడుతోంది…', error: 'ప్రస్తుతం అనువాదం అందుబాటులో లేదు. మళ్లీ ప్రయత్నించండి.' },
  { code: 'ta', label: 'தமிழ்', summaryTitle: 'எளிய சொற்களில்', languageLabel: 'மொழி', loading: 'சுருக்கம் மொழிபெயர்க்கப்படுகிறது…', error: 'இப்போது மொழிபெயர்ப்பு கிடைக்கவில்லை. மீண்டும் முயற்சிக்கவும்.' },
];

function formatNumber(value, maximumFractionDigits = 1) {
  return new Intl.NumberFormat('en-IN', { maximumFractionDigits }).format(value);
}

export function buildFarmerSummary(type, data) {
  if (type === 'disease') {
    const healthy = data.prediction.toLowerCase().includes('healthy');
    const diagnosis = data.prediction
      .replace(/___/g, ': ')
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (letter) => letter.toUpperCase());
    const confidence = formatNumber(data.confidence * 100);
    return healthy
      ? `The leaf photo looks healthy. The closest match is ${diagnosis}, with ${confidence}% confidence. Keep watching the plant, and ask a local agriculture officer if symptoms appear.`
      : `The leaf photo may show signs of disease. The closest match is ${diagnosis}, with ${confidence}% confidence. This photo check is not final, so ask a local agriculture officer before choosing treatment.`;
  }

  if (type === 'crop') {
    const details = data.usesSoilWeather
      ? 'The ranking also includes the soil and weather details you entered.'
      : 'The ranking is based on past local crop records.';
    return `For ${data.district}, ${data.state}, ${data.recommendedCrop} ranked first. ${details} This is guidance, not a promise of a good harvest. Before planting, consider water availability this season, a soil test, and local farming advice.`;
  }

  if (type === 'yield') {
    const season = data.season.trim();
    const estimate = formatNumber(data.estimate, 2);
    const lower = formatNumber(data.lower, 2);
    const upper = formatNumber(data.upper, 2);
    const confidence = formatNumber(data.confidence * 100, 0);
    return `For ${data.crop} in ${data.state} during ${season}, the estimated harvest is ${estimate} tonnes per hectare. At the selected ${confidence}% confidence level, past model results suggest the harvest may be between ${lower} and ${upper} tonnes per hectare. This is an estimate, not a guarantee; weather, soil, and farming practices can change the harvest.`;
  }

  throw new Error(`Unknown farmer summary type: ${type}`);
}
