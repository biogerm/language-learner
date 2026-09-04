export function formatWordPrompt(record: {
  word_in_sentence?: string;
  base_form?: string;
  en_translation?: string;
  contextual_en?: string | null;
  dict_en?: string;
}, dictionary?: Record<string, any> | null): string {
  let contextual = (record.contextual_en || record.en_translation || '').trim();
  const baseForm = (record.base_form || '').trim().toLowerCase();
  let dictEn = (record.dict_en || (record.en_translation && record.contextual_en && record.en_translation.toLowerCase() !== record.contextual_en.toLowerCase() ? record.en_translation : '') || (baseForm ? dictionary?.[baseForm] : '') || '').trim();

  // Sanity check for historical dictionary typo
  if (baseForm === 'fortfarande') {
    if (dictEn === 'sill') dictEn = 'still';
    if (contextual === 'sill') contextual = 'still';
  }

  // If contextual meaning is present and differs from dictionary definition of the base form:
  if (contextual && dictEn && contextual.toLowerCase() !== dictEn.toLowerCase()) {
    const wordInSent = (record.word_in_sentence || '').trim().toLowerCase();
    const isInflectedVariant = Boolean(wordInSent && baseForm && wordInSent !== baseForm);
    if (isInflectedVariant) {
      return `${contextual} (base form: ${dictEn})`;
    }
    return `${contextual} (${dictEn})`;
  }

  // Pure single English definition
  return contextual || dictEn || record.word_in_sentence || record.base_form || '';
}
