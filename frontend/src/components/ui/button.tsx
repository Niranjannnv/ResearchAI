import * as React from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline" | "ghost" | "secondary" | "destructive";
  size?: "default" | "sm" | "lg" | "icon";
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", ...props }, ref) => {
    const baseStyles = "inline-flex items-center justify-center rounded-xl text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 disabled:pointer-events-none disabled:opacity-50 select-none";
    
    const variants = {
      default: "bg-emerald-600 text-white hover:bg-emerald-700 shadow-sm",
      outline: "border border-gray-200 bg-white text-gray-700 hover:bg-gray-50 hover:border-gray-300",
      secondary: "bg-gray-100 text-gray-900 hover:bg-gray-200",
      ghost: "text-gray-600 hover:bg-gray-100 hover:text-gray-900",
      destructive: "bg-red-50 text-red-600 hover:bg-red-100 border border-red-200",
    };

    const sizes = {
      default: "h-10 px-4 py-2",
      sm: "h-8 rounded-lg px-3 text-xs",
      lg: "h-12 rounded-2xl px-6 text-base",
      icon: "h-9 w-9 rounded-lg",
    };

    return (
      <button
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button };
