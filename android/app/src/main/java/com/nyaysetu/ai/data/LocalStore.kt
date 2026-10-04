package com.nyaysetu.ai.data

import android.content.Context
import androidx.room.*
import kotlinx.coroutines.flow.Flow

@Entity(tableName="incidents")
data class IncidentEntity(
    @PrimaryKey val id:String,
    val title:String,
    val category:String,
    val severity:String,
    val summary:String,
    val createdAt:Long=System.currentTimeMillis(),
    val status:String="ACTIVE"
)

@Entity(tableName="evidence")
data class EvidenceEntity(
    @PrimaryKey val id:String,
    val incidentId:String,
    val name:String,
    val type:String,
    val hash:String,
    val localPath:String="",
    val createdAt:Long=System.currentTimeMillis(),
    val note:String=""
)

@Dao interface IncidentDao{
    @Query("SELECT * FROM incidents ORDER BY createdAt DESC") fun observeAll():Flow<List<IncidentEntity>>
    @Insert(onConflict=OnConflictStrategy.REPLACE) fun insert(item:IncidentEntity)
    @Delete fun delete(item:IncidentEntity)
    @Query("UPDATE incidents SET status=:status WHERE id=:id") fun updateStatus(id:String,status:String)
    @Query("DELETE FROM incidents") fun deleteAll()
}
@Dao interface EvidenceDao{
    @Query("SELECT * FROM evidence ORDER BY createdAt DESC") fun observeAll():Flow<List<EvidenceEntity>>
    @Insert(onConflict=OnConflictStrategy.REPLACE) fun insert(item:EvidenceEntity)
    @Delete fun delete(item:EvidenceEntity)
    @Query("DELETE FROM evidence") fun deleteAll()
}

@Database(entities=[IncidentEntity::class,EvidenceEntity::class],version=2,exportSchema=false)
abstract class AppDatabase:RoomDatabase(){
    abstract fun incidents():IncidentDao
    abstract fun evidence():EvidenceDao
    companion object{fun create(context:Context)=Room.databaseBuilder(context,AppDatabase::class.java,"nyaysetu.db").fallbackToDestructiveMigration().build()}
}
