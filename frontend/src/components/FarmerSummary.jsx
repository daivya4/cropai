import React, { useEffect, useMemo, useState } from 'react';
import { api } from '../api/client';
import { buildFarmerSummary, SUMMARY_LANGUAGES } from '../i18n/farmerSummaries';

export function FarmerSummary({ type, data }) {
  const [language, setLanguage] = useState('en');
  const [translation, setTranslation] = useState(null);
  const [translationErrorKey, setTranslationErrorKey] = useState(null);
  const dataKey = JSON.stringify(data);
  const englishSummary = useMemo(
    () => buildFarmerSummary(type, JSON.parse(dataKey)),
    [type, dataKey],
  );
  const languageDetails = SUMMARY_LANGUAGES.find((item) => item.code === language);
  const translationKey = `${language}\u0000${englishSummary}`;

  useEffect(() => {
    if (language === 'en') {
      return undefined;
    }

    const controller = new AbortController();

    api.translateSummary({
      text: englishSummary,
      language,
      signal: controller.signal,
    })
      .then(({ translated_text: text }) => {
        if (!controller.signal.aborted) {
          setTranslation({ key: translationKey, text });
        }
      })
      .catch((error) => {
        if (error.name !== 'CanceledError' && error.name !== 'AbortError') {
          setTranslationErrorKey(translationKey);
        }
      });

    return () => controller.abort();
  }, [englishSummary, language, translationKey]);

  const summaryText = language === 'en'
    ? englishSummary
    : translation?.key === translationKey
      ? translation.text
      : translationErrorKey === translationKey
        ? languageDetails.error
        : languageDetails.loading;

  return (
    <section className="farmer-summary" aria-live="polite">
      <div className="farmer-summary-header">
        <h3>{languageDetails.summaryTitle}</h3>
        <label className="farmer-summary-language">
          <span>{languageDetails.languageLabel}</span>
          <select
            value={language}
            onChange={(event) => setLanguage(event.target.value)}
            aria-label={languageDetails.languageLabel}
          >
            {SUMMARY_LANGUAGES.map((item) => (
              <option key={item.code} value={item.code}>{item.label}</option>
            ))}
          </select>
        </label>
      </div>
      <p>{summaryText}</p>
    </section>
  );
}

export default FarmerSummary;
