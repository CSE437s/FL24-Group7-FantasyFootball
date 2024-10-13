// lib/yahoo-fantasy-wrapper.ts
export const YahooFantasy = async () => {
  const module = await import('yahoo-fantasy');
  return module?.default || module;
};
