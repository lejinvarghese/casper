import React from "react";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
    children?: React.ReactNode;
}

interface IconProps extends React.SVGProps<SVGSVGElement> {
    size?: number;
}

const Card: React.FC<CardProps> = ({ children, className, ...props }) => (
    <div className={`border rounded-lg ${className}`} {...props}>
        {children}
    </div>
);

const CardHeader: React.FC<CardProps> = ({ children, className, ...props }) => (
    <div className={`p-4 border-b ${className}`} {...props}>
        {children}
    </div>
);

const CardTitle: React.FC<CardProps> = ({ children, className, ...props }) => (
    <h3 className={`text-xl font-semibold ${className}`} {...props}>
        {children}
    </h3>
);

const CardContent: React.FC<CardProps> = ({
    children,
    className,
    ...props
}) => (
    <div className={`p-4 ${className}`} {...props}>
        {children}
    </div>
);

export { Card, CardHeader, CardTitle, CardContent };
