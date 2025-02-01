import React from "react";
import { motion } from "framer-motion";

export const AnimatedBackground: React.FC = () => {
    return (
        <svg
            className="fixed inset-0 z-0 w-full h-full"
            style={{ pointerEvents: "none" }}
        >
            <defs>
                <filter id="blurFilter">
                    <feGaussianBlur in="SourceGraphic" stdDeviation="0.1" />
                </filter>
            </defs>
            {[...Array(50)].map((_, index) => {
                const x = Math.random() * 100;
                const y = Math.random() * 100;
                const size = Math.random() * 10 + 2;
                const opacity = Math.random() * 0.5 + 0.1;
                const animationDelay = Math.random() * 5;

                return (
                    <motion.circle
                        key={index}
                        cx={`${x}%`}
                        cy={`${y}%`}
                        r={size / 2}
                        fill="#4287f5"
                        opacity={opacity}
                        initial={{ scale: 0 }}
                        animate={{
                            scale: [0, 1.5, 1],
                            x: [`${x}%`, `${x + (Math.random() * 10 - 5)}%`],
                            y: [`${y}%`, `${y + (Math.random() * 10 - 5)}%`],
                        }}
                        transition={{
                            duration: 5,
                            repeat: Infinity,
                            repeatType: "reverse",
                            delay: animationDelay,
                        }}
                        style={{ filter: "url(#blurFilter)" }}
                    />
                );
            })}
        </svg>
    );
};