import React from "react";
import Hero from "./Hero";
import Catalogo from "./Catalogo";
import About from "./About";
import Features from "./Features";
import Social from "./Social";


export default function Home() {
    return (
        <main>
            <Hero />
            <section>
                <Catalogo />
            </section>
            <section className="relative z-10 bg-black mt-[-50vh]">
                <About />
            </section>
            <section>
                <Features />
            </section>
            <section>
                <Social />
            </section>
        </main>
    )
}



