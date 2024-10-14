export const YahooFantasy = async () => {
    const module = await import('yahoo-fantasy/dist/YahooFantasy.mjs');
    return module.default;
  };
  