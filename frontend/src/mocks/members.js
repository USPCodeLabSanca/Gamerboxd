export const members = Array.from(
  { length: 100 },
  (_, index) => ({
    id: index + 1,
    name: `Usuário ${index + 1}`,
    gamesPlayed: Math.floor(Math.random() * 2000),
    reviews: Math.floor(Math.random() * 1000),
    likes: Math.floor(Math.random() * 5000),
    profilePicture: `https://i.pravatar.cc/300?img=${(index % 70) + 1}`,
  })
);
