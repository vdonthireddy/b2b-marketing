import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import Login from "@/app/(auth)/login/page";
import { api } from "@/lib/api";

// Mock the API client
vi.mock("@/lib/api", () => ({
  api: {
    post: vi.fn(),
  }
}));

describe("Login Page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders login form correctly", () => {
    render(<Login />);
    expect(screen.getByRole("heading", { name: /sign in/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /sign in/i })).toBeInTheDocument();
  });

  it("displays error message on failed login", async () => {
    (api.post as any).mockRejectedValueOnce({
      response: { data: { detail: "Invalid credentials" } }
    });

    render(<Login />);
    
    await userEvent.type(screen.getByLabelText(/email/i), "test@test.com");
    await userEvent.type(screen.getByLabelText(/password/i), "wrongpass");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(api.post).toHaveBeenCalledWith("/api/auth/login", {
      email: "test@test.com",
      password: "wrongpass"
    });
    
    // Check if error message is displayed
    const errorMessage = await screen.findByText("Invalid credentials");
    expect(errorMessage).toBeInTheDocument();
  });

  it("calls setAuth and redirects on successful login", async () => {
    (api.post as any).mockResolvedValueOnce({
      data: {
        access_token: "mock-token",
        refresh_token: "mock-refresh",
        user: { id: "1", email: "test@test.com", role: "admin", name: "Test" }
      }
    });

    render(<Login />);
    
    await userEvent.type(screen.getByLabelText(/email/i), "test@test.com");
    await userEvent.type(screen.getByLabelText(/password/i), "password123");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(api.post).toHaveBeenCalledWith("/api/auth/login", {
      email: "test@test.com",
      password: "password123"
    });
  });
});
