export const avatarOptions = Array.from({ length: 12 }, (_, index) => {
  const numero = index + 1;

  return {
    id: `avatar-${numero}`,
    url: `/presets/avatares/avatar${numero}.png`,
    name: `Avatar ${numero}`
  };
});

export const bannerOptions = Array.from({ length: 12 }, (_, index) => {
  const numero = index + 1;

  return {
    id: `banner-${numero}`,
    url: `/presets/banners/banner${numero}.png`,
    name: `Banner ${numero}`
  };
});