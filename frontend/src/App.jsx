import { BrowserRouter, Routes, Route } from "react-router-dom"
import { ParallaxProvider } from 'react-scroll-parallax';
import Home from "./pages/home"
import Login from "./pages/login"
import Register from "./pages/register"
import Games from "./pages/games"
import GamePage from "./pages/gamePage"
import Feed from "./pages/feed"
import Profile from "./pages/profile"
import Members from "./pages/members"
import MembersList from "./pages/membersList"
import Lists from "./pages/lists"
import ListDetail from "./pages/listDetail";
import Navbar from "./components/Navbar"
import Footer from "./components/Footer"

export default function App() {
  return (
    <ParallaxProvider>

      <BrowserRouter>

        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/games" element={<Games />} />
          <Route path="/games/:id" element={<GamePage />} />
          <Route path="/members" element={<Members />} />
          <Route path="/members/all" element={<MembersList />} />
          <Route path="/lists" element={<Lists />} />
          <Route path="/lists/:id" element={<ListDetail />} />
          <Route path="/profile/:username" element={<Profile />} />
          {/*
          <Route path="/games/:slug" element={<GamePage />} />
          <Route path="/feed" element={<Feed />} />
          <Route path="/profile/:username" element={<Profile />} />
          <Route path="/members" element={<Members />} />
          <Route path="/lists" element={<Lists />} /> */}
        </Routes>
        <Footer />
      </BrowserRouter>
    </ParallaxProvider>
  )
}
