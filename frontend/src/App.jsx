import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/home";
import Login from "./pages/login";
import Register from "./pages/register";
import Games from "./pages/games";
import GamePage from "./pages/gamePage";
import Feed from "./pages/feed";
import Profile from "./pages/profile";
import Members from "./pages/members";
import Lists from "./pages/lists";
import Navbar from "./components/Navbar";

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />

      <Routes>
        <Route path="/home" element={<Home />} />

        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        {/*
        <Route path="/games" element={<Games />} />
        <Route path="/games/:slug" element={<GamePage />} />
        <Route path="/feed" element={<Feed />} />
        <Route path="/profile/:username" element={<Profile />} />
        <Route path="/members" element={<Members />} />
        <Route path="/lists" element={<Lists />} />
        */}
      </Routes>
    </BrowserRouter>
  );
}
