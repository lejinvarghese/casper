import React from "react";
import { motion } from "framer-motion";
import { BookOpen, CalendarDays, Link2 } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "./Card";
import { Paper, LucideIcon, domainIcons } from "../types";

interface PaperCardProps {
    paper: Paper;
    index: number;
}

export const PaperCard: React.FC<PaperCardProps> = ({ paper, index }) => {
    const DomainIcon: LucideIcon = domainIcons[paper.domain] || BookOpen;

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{
                delay: index * 0.2,
                type: "spring",
                stiffness: 100,
            }}
            className="relative z-20"
        >
            <Card className="h-full flex flex-col bg-white/80 backdrop-blur-sm shadow-lg hover:shadow-2xl transition-all duration-300">
                <CardHeader className="flex flex-row items-center space-x-4 border-b pb-3">
                    <div className="bg-blue-100 p-3 rounded-full">
                        <DomainIcon className="text-blue-600" size={24} />
                    </div>
                    <CardTitle className="text-xl font-semibold text-gray-900">
                        {paper.title}
                    </CardTitle>
                </CardHeader>
                <CardContent className="flex-grow flex flex-col justify-between p-6">
                    <div className="mb-4">
                        <p className="text-gray-600 mb-4 line-clamp-3">
                            {paper.summary}
                        </p>
                    </div>

                    <div className="flex justify-between items-center text-gray-500">
                        <div className="flex items-center space-x-2">
                            <CalendarDays size={16} />
                            <span className="text-sm">
                                {new Date(paper.publishedDate).toLocaleDateString()}
                            </span>
                        </div>

                        <a
                            href={paper.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center space-x-2 text-blue-600 hover:text-blue-800"
                        >
                            <Link2 size={16} />
                            <span className="text-sm">View Paper</span>
                        </a>
                    </div>
                </CardContent>
            </Card>
        </motion.div>
    );
};