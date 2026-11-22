// SPDX-License-Identifier: AGPL-3.0-or-later
import { test, expect, jest } from "@jest/globals";
import "@testing-library/jest-dom/jest-globals";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

test("Button renders with aria-label and fires onClick", async () => {
  const onClick = jest.fn();
  render(
    <Button aria-label="Save protocol" onClick={onClick}>
      Save
    </Button>,
  );
  await userEvent.click(screen.getByRole("button", { name: "Save protocol" }));
  expect(onClick).toHaveBeenCalledTimes(1);
});

test("Input renders its label", () => {
  render(<Input label="Email" />);
  expect(screen.getByLabelText("Email")).toBeInTheDocument();
});

test("Input error is shown and linked via aria-describedby", () => {
  render(<Input label="Email" error="Required" />);
  const input = screen.getByLabelText("Email");
  const err = screen.getByText("Required");
  expect(input).toHaveAttribute("aria-describedby", err.id);
});
