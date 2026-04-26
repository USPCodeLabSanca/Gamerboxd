import React from "react";
import Hero from "./Hero";
import Catalogo from "./Catalogo";
import About from "./About";


export default function Home() {
    return (
        <main>
            <Hero />
            <div>
                <Catalogo />
            </div>
            <div className="relative z-10 bg-black mt-[-50vh]">
                <About />
            </div>
        </main>
    )
}



