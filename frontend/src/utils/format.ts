export function formatWordPrompt(record: {
  word_in_sentence?: string;
  base_form?: string;
  en_translation?: string;
  contextual_en?: string | null;
  dict_en?: string;
}, dictionary?: Record<string, any> | null): string {
  const contextual = (record.contextual_en || record.en_translation || '').trim();
  const baseForm = (record.base_form || '').trim().toLowerCase();
  const dictEn = (record.dict_en || (record.en_translation && record.contextual_en && record.en_translation.toLowerCase() !== record.contextual_en.toLowerCase() ? record.en_translation : '') || (baseForm ? dictionary?.[baseForm] : '') || '').trim();

  // If contextual meaning is present and differs from dictionary definition of the base form:
  // Explicitly state "(base form: <dictEn>)" in pure English without leaking Swedish lemma
  if (contextual && dictEn && contextual.toLowerCase() !== dictEn.toLowerCase()) {
    return `${contextual} (base form: ${dictEn})`;
  }

  // Pure single English definition
  return contextual || dictEn || 'Custom Word';
}
