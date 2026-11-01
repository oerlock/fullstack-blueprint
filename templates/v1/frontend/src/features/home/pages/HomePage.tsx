import { useState } from 'react'
import heroImg from '../../../assets/images/hero.png'
import '../../../assets/styles/home.css'

export function HomePage() {
  const [count, setCount] = useState(0)

  return (
    <>
      <section id="center">
        <div className="hero">
          <img src={heroImg} className="base" width="170" height="179" alt="" />
        </div>
        <div>
          <h1>Get started</h1>
          <p>
            Edit <code>src/features/home/pages/HomePage.tsx</code> and save to
            test <code>HMR</code>
          </p>
        </div>
        <button
          type="button"
          className="counter"
          onClick={() => setCount((count) => count + 1)}
        >
          Count is {count}
        </button>
      </section>

      <div className="ticks"></div>
      <section id="spacer"></section>
    </>
  )
}
