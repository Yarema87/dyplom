import Link from "next/link";

function Header() {
    return(
        <div>
            <Link href='/login'>Log in</Link>
            <Link href='/signup'>Sign up</Link>
        </div>
    )
}

export default Header;