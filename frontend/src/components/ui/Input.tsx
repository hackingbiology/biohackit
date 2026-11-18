// SPDX-License-Identifier: AGPL-3.0-or-later
// biohack.it — open-source biohacking platform
// Copyright (C) HackingBiology 2026 — https://biohack.it
// Full license text: https://www.gnu.org/licenses/agpl-3.0.html

import { InputHTMLAttributes, forwardRef } from "react";

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, id, className = "", ...props }, ref) => {
    const inputId = id ?? label.toLowerCase().replace(/\s+/g, "-");
    const errorId = error ? `${inputId}-error` : undefined;

    return (
      <div className="space-y-1">
        <label htmlFor={inputId} className="block text-sm font-medium">
          {label}
        </label>
        <input
          ref={ref}
          id={inputId}
          aria-describedby={errorId}
          aria-invalid={!!error}
          className={`block w-full rounded-lg border px-3 py-2 text-sm bg-transparent focus:outline-none focus:ring-2 focus:ring-slate-500 ${
            error
              ? "border-red-500 focus:ring-red-500"
              : "border-slate-300 dark:border-slate-600"
          } ${className}`}
          {...props}
        />
        {error && (
          <p id={errorId} role="alert" className="text-xs text-red-600">
            {error}
          </p>
        )}
      </div>
    );
  },
);
Input.displayName = "Input";

export { Input };
