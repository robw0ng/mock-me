import Sidebar from "../components/Sidebar"

export default function Dashboard() {
    return (
        <div className="flex w-screen justify-center">
            <div className="flex h-screen">
                <Sidebar />
            </div>
            
            <div className="flex flex-1 justify-center items-center">
                Main Area
            </div>
        </div>
    )
}